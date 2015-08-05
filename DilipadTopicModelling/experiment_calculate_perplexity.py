import pandas as pd
import logging
from multiprocessing import Pool

from CPTCorpus import CPTCorpus
from CPT_Gibbs import GibbsSampler


def calculate_perplexity(corpus, nTopics, nIter, beta, out_dir, nPerplexity):
    alpha = 50.0/nTopics
    sampler = GibbsSampler(corpus, nTopics=nTopics, nIter=nIter,
                           alpha=alpha, beta=beta, beta_o=beta,
                           out_dir=out_dir.format(nTopics))
    sampler._initialize()
    #sampler.run()
    results = []
    print nPerplexity
    for s in nPerplexity:
        logger.info('doing perplexity calculation ({}, {})'.format(nTopics, s))
        tw_perp, ow_perp = sampler.perplexity(index=s)
        results.append((nTopics, s, tw_perp, ow_perp))
    logger.info('finished perplexity calculation for {} topics'.
                format(nTopics))
    return results


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)

logging.getLogger('gensim').setLevel(logging.ERROR)
logging.getLogger('CPTCorpus').setLevel(logging.ERROR)
logging.getLogger('CPT_Gibbs').setLevel(logging.ERROR)

# load corpus
data_dir = '/home/jvdzwaan/data/tmp/generated/test_exp/'
corpus = CPTCorpus.load('{}corpus.json'.format(data_dir),
                        topicDict='{}/topicDict.dict'.format(data_dir),
                        opinionDict='{}/opinionDict.dict'.format(data_dir))

nIter = 200
beta = 0.02
out_dir = '/home/jvdzwaan/data/tmp/generated/test_exp/{}'

nTopics = range(20, nIter+1, 20)
nPerplexity = range(0, nIter+1, 10)

# calculate perplexity
pool = Pool(processes=5)
results = [pool.apply_async(calculate_perplexity, args=(corpus, n, nIter, beta,
                            out_dir, nPerplexity))
           # reverse list, so longest calculation is started first
           for n in nTopics[::-1]]
pool.close()
pool.join()

# aggrate and save results
data = [p.get() for p in results]

topic_perp = pd.DataFrame(columns=nTopics, index=nPerplexity)
opinion_perp = pd.DataFrame(columns=nTopics, index=nPerplexity)

for result in data:
    for n, s, tw_perp, ow_perp in result:
        topic_perp.set_value(s, n, tw_perp)
        opinion_perp.set_value(s, n, ow_perp)

topic_perp.to_csv(out_dir.format('perplexity_topic.csv'))
opinion_perp.to_csv(out_dir.format('perplexity_opinion.csv'))