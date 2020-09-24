# coding: utf-8
import numpy as np
import tensorflow as tf
from gpflow import default_float, default_jitter

from . import assigngp_dense


class AssignGPSparse(assigngp_dense.AssignGP):
    r"""
    Gaussian Process sparse regression, but where the index to which the data are
    assigned is unknown.

    let f be a vector of GP points (usually longer than the number of data)

        f ~ MVN(0, K)

    and let Z be an (unknown) binary matrix with a single 1 in each row. The
    likelihood is

       y ~ MVN( Z f, \sigma^2 I)

    That is, each element of y is a noisy realization of one (unknown) element
    of f. We use variational Bayes to infer the labels using a sparse prior
    over the Z matrix (i.e. we have narrowed down the choice of which function
    values each y is drawn from).

    """

    def __init__(
        self,
        t,
        XExpanded,
        Y,
        kern,
        indices,
        b,
        ZExpanded,
        fDebug=False,
        phiInitial=None,
        phiPrior=None,
    ):
        assigngp_dense.AssignGP.__init__(
            self,
            t,
            XExpanded,
            Y,
            kern,
            indices,
            b,
            fDebug=fDebug,
            phiInitial=phiInitial,
            phiPrior=phiPrior,
        )
        # Do not treat inducing points as parameters because they should always be fixed.
        self.ZExpanded = ZExpanded  # inducing points for sparse GP. Same as XExpanded
        # TODO: these were DataHolder in GPflow1, should they change

        assert ZExpanded.shape[1] == XExpanded.shape[1]

    def _build_likelihood(self):
        if self.fDebug:
            print("assignegp_denseSparse compiling model (build_likelihood)")
        N = tf.cast(tf.shape(self.Y)[0], dtype=default_float())
        M = tf.shape(self.ZExpanded)[0]
        D = tf.cast(tf.shape(self.Y)[1], dtype=default_float())

        Phi = tf.nn.softmax(self.logPhi)
        # try squashing Phi to avoid numerical errors
        Phi = (1 - 2e-6) * Phi + 1e-6

        sigma2 = self.likelihood.variance
        sigma = tf.sqrt(self.likelihood.variance)
        Kuu = (
            self.kern.K(self.ZExpanded)
            + tf.eye(M, dtype=default_float()) * default_jitter()
        )
        Kuf = self.kern.K(self.ZExpanded, self.X)

        Kdiag = self.kern.Kdiag(self.X)
        L = tf.cholesky(Kuu)
        A = tf.reduce_sum(Phi, 0)
        LiKuf = tf.matrix_triangular_solve(L, Kuf)
        W = LiKuf * tf.sqrt(A) / sigma
        P = tf.matmul(W, tf.transpose(W)) + tf.eye(M, dtype=default_float())
        traceTerm = -0.5 * tf.reduce_sum(Kdiag * A) / sigma2 + 0.5 * tf.reduce_sum(
            tf.square(W)
        )
        R = tf.cholesky(P)
        tmp = tf.matmul(LiKuf, tf.matmul(tf.transpose(Phi), self.Y))
        c = tf.matrix_triangular_solve(R, tmp, lower=True) / sigma2
        if self.fDebug:
            # trace term should be 0 for Z=X (full data)
            traceTerm = tf.Print(
                traceTerm,
                [traceTerm],
                message="traceTerm=",
                name="traceTerm",
                summarize=10,
            )

        self.bound = (
            traceTerm
            - 0.5 * N * D * tf.log(2 * np.pi * sigma2)
            - 0.5 * D * tf.reduce_sum(tf.log(tf.square(tf.diag_part(R))))
            - 0.5 * tf.reduce_sum(tf.square(self.Y)) / sigma2
            + 0.5 * tf.reduce_sum(tf.square(c))
            - self.build_KL(Phi)
        )

        return self.bound

    def _build_predict(self, Xnew, full_cov=False):
        M = tf.shape(self.ZExpanded)[0]

        Phi = tf.nn.softmax(self.logPhi)
        # try squashing Phi to avoid numerical errors
        Phi = (1 - 2e-6) * Phi + 1e-6

        sigma2 = self.likelihood.variance
        sigma = tf.sqrt(sigma2)
        Kuu = (
            self.kern.K(self.ZExpanded)
            + tf.eye(M, dtype=default_float()) * default_jitter()
        )
        Kuf = self.kern.K(self.ZExpanded, self.X)
        L = tf.cholesky(Kuu)

        p = tf.reduce_sum(Phi, 0)
        LiKuf = tf.matrix_triangular_solve(L, Kuf)
        W = LiKuf * tf.sqrt(p) / sigma
        P = tf.matmul(W, tf.transpose(W)) + tf.eye(M, dtype=default_float())
        R = tf.cholesky(P)
        tmp = tf.matmul(LiKuf, tf.matmul(tf.transpose(Phi), self.Y))
        c = tf.matrix_triangular_solve(R, tmp, lower=True) / sigma2

        Kus = self.kern.K(self.ZExpanded, Xnew)
        tmp1 = tf.matrix_triangular_solve(L, Kus, lower=True)
        tmp2 = tf.matrix_triangular_solve(R, tmp1, lower=True)
        mean = tf.matmul(tf.transpose(tmp2), c)
        if full_cov:
            var = (
                self.kern.K(Xnew)
                + tf.matmul(tf.transpose(tmp2), tmp2)
                - tf.matmul(tf.transpose(tmp1), tmp1)
            )
            shape = tf.stack([1, 1, tf.shape(self.Y)[1]])
            var = tf.tile(tf.expand_dims(var, 2), shape)
        else:
            var = (
                self.kern.Kdiag(Xnew)
                + tf.reduce_sum(tf.square(tmp2), 0)
                - tf.reduce_sum(tf.square(tmp1), 0)
            )
            shape = tf.stack([1, tf.shape(self.Y)[1]])
            var = tf.tile(tf.expand_dims(var, 1), shape)
        return mean, var
