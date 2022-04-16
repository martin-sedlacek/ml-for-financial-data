import numpy as np
from sklearn.metrics import auc
import torch


def excess_mass(t, t_max, volume_support, s_unif, s_X, n_generated):
    EM_t = np.zeros(t.shape[0])
    n_samples = s_X.shape[0]
    s_X_unique = np.unique(s_X)
    EM_t[0] = 1.

    for u in s_X_unique:
        EM_t = np.maximum(EM_t, 1. / n_samples * (s_X > u).sum() -
                        t * (s_unif > u).sum() / n_generated
                        * volume_support)
    amax = np.argmax(EM_t <= t_max) + 1
    if amax == 1:
        amax = -1 # failed to achieve t_max
    AUC = auc(t[:amax], EM_t[:amax])
    return AUC, EM_t, amax


def mass_volume(axis_alpha, volume_support, s_unif, s_X, n_generated):
    n_samples = s_X.shape[0]
    s_X_argsort = s_X.argsort()
    mass = 0
    cpt = 0
    u = s_X[s_X_argsort[-1]]
    mv = np.zeros(axis_alpha.shape[0])
    for i in range(axis_alpha.shape[0]):
        while mass < axis_alpha[i]:
            cpt += 1
            u = s_X[s_X_argsort[-cpt]]
            mass = 1. / n_samples * cpt  # sum(s_X > u)
        mv[i] = float((s_unif >= float(u)).sum()) / n_generated * volume_support
    return auc(axis_alpha, mv), mv


def emmv_scores(trained_model, df, scoring_func=None, n_generated=10000, alpha_min=0.9, alpha_max=0.999, t_max=0.9):
    """Get Excess-Mass (EM) and Mass Volume (MV) scores for unsupervised ML AD models.
    :param trained_model: Trained ML model with a 'decision_function' method
    :param df: Pandas dataframe of features (X matrix)
    :param scoring_func: Anomaly scoring function (callable)
    :param n_generated: , defaults to 10000
    :param alpha_min: Min value for alpha axis, defaults to 0.9
    :param alpha_max: Max value for alpha axis, defaults to 0.999
    :param t_max: Min EM value required, defaults to 0.9
    :return: A dictionary of two scores ('em' and 'mv')
    """

    if scoring_func is None:
        scoring_func = lambda model, df: model.decision_function(df)

    # Get limits and volume support.
    lim_inf = df.min(axis=0)
    lim_sup = df.max(axis=0)
    print(lim_inf.shape)
    offset = 1e-60 # to prevent division by 0
    try:
        volume_support = (lim_sup - lim_inf).prod() + offset
    except AttributeError as e: # i.e Pandas Series
        volume_support = (lim_sup - lim_inf) + offset
    print(volume_support)
    # Determine EM and MV parameters
    t = np.arange(0, 100 / volume_support, 0.01 / volume_support)
    axis_alpha = np.arange(alpha_min, alpha_max, 0.0001)
    try:
        unif = np.random.uniform(lim_inf, lim_sup, size=(n_generated, df.shape[1]))
    except IndexError as e: # i.e. 1D data
        unif = np.random.uniform(lim_inf, lim_sup, size=(n_generated))

    # Get anomaly scores
    anomaly_score = scoring_func(trained_model, df)#.reshape(1, -1)[0]
    s_unif = scoring_func(trained_model, unif)

    # Get EM and MV scores
    AUC_em, em, amax = excess_mass(t, t_max, volume_support, s_unif, anomaly_score, n_generated)
    AUC_mv, mv = mass_volume(axis_alpha, volume_support, s_unif, anomaly_score, n_generated)
    # Return a dataframe containing EMMV information
    scores = {
        'em': np.mean(em),
        'mv': np.mean(mv),
    }
    return scores


def torch_emmv_scores(trained_model, x, scoring_func=None, n_generated=10000, alpha_min=0.9, alpha_max=0.999,
                      t_max=0.9):
    # Get limits and volume support.
    lim_inf = torch.min(x.view(-1, 6), dim=0)[0]
    lim_sup = torch.max(x.view(-1, 6), dim=0)[0]
    offset = 1e-60  # to prevent division by 0

    # Volume support
    volume_support = torch.prod(lim_sup - lim_inf).item() + offset

    # Determine EM and MV parameters
    t = np.arange(0, 100 / volume_support, 0.01 / volume_support)
    axis_alpha = np.arange(alpha_min, alpha_max, 0.0001)

    unif = torch.rand(n_generated, x.size(1), x.size(2))
    m = lim_sup - lim_inf
    unif = unif * m
    unif = unif + lim_inf

    # Get anomaly scores
    anomaly_score = scoring_func(trained_model, x).view(-1, 1).detach().numpy()
    s_unif = scoring_func(trained_model, unif).view(-1, 1).detach().numpy()

    # Get EM and MV scores
    AUC_em, em, amax = excess_mass(t, t_max, volume_support, s_unif, anomaly_score, n_generated)
    AUC_mv, mv = mass_volume(axis_alpha, volume_support, s_unif, anomaly_score, n_generated)

    # Return a dataframe containing EMMV information
    scores = {
        'em': np.mean(em),
        'mv': np.mean(mv),
    }
    return scores


def metric_calc(y_hat, y):
    true_positives = true_negatives = false_positives = false_negatives = 0
    for i in range(y.size(0)):
        for j in range(y.size(1)):
            cur_label = y[i][j].item()
            cur_pred = y_hat[i][j].item()
            if cur_label == 1 and cur_pred == 1:
                true_positives += 1
            elif cur_label == 1 and cur_pred == 0:
                false_negatives += 1
            elif cur_label == 0 and cur_pred == 1:
                false_positives += 1
            else:
                true_negatives += 1
    return true_positives, true_negatives, false_positives, false_negatives


def accuracy(true_positives, true_negatives, y):
    return (true_positives+true_negatives) / (y.size(0)*y.size(1))


def precision(true_positives, false_positives):
    return true_positives / (true_positives+false_positives)


def recall(true_positives, false_negatives):
    return true_positives / (true_positives+false_negatives)
