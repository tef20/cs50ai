import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # form transition model with equal distribution
    base_model = base_trans_model(corpus, damping_factor)

    # update probabilities based on links from current page
    trans_model = linked_trans_model(base_model, corpus, page, damping_factor)

    return trans_model


def base_trans_model(corpus, damping_factor):
    """
    Generate base transition model with equal probabilities for
    all pages.
    """
    pages = list(corpus.keys())

    # dampened probability of randomly jumping to any page
    reach_by_jump = (1 - damping_factor) / len(pages)

    # form base transition model
    trans_model = {k:reach_by_jump for k in pages}

    return trans_model


def linked_trans_model(model, corpus, page, damping_factor):
    """
    Update transition model with probabilities for pages reachable 
    by link.
    """
    # set of pages linked to by current page
    links = {link for link in corpus[page] if link != page}

    # dampened probability of reaching a page via page link
    reach_by_link = damping_factor / len(links)

    # complete transition model with linked page probabilities
    for link in links:
        model[link] += reach_by_link

    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    p_ranks = dict()

    # chose initial random page in corpus
    move = random.choice(pages)

    # get PageRanks over sample of n
    normalised_increment = 1 / n
    for i in range(n):
        # random surf to next page
        move = choose_page(corpus, damping_factor, pages, move)
        # add count for that page
        if move in p_ranks:
            p_ranks[move] += normalised_increment
        else:
            p_ranks[move] = normalised_increment

    # check sum = ~1
    # pr_sum = 0
    # for pr in p_ranks:
    #     pr_sum += p_ranks[pr]
    # print(pr_sum)
    # assert 0.999 < pr_sum < 1.001, "PR sum not between 0.999 and 1.001."

    return p_ranks


def choose_page(corpus, damping_factor, pages, move):
    # generate transition model for current page
    distributions = transition_model(corpus, move, damping_factor)

    # select random page, based on transition model weights
    return random.choices(pages, list(distributions.values()))[0]


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Start assuming PageRank for each page is 1 / all pages
    pages = corpus.keys()
    base_page_rank = 1 / len(pages)

    # initialise page rank
    page_ranks = {k:base_page_rank for k in corpus}
    new_pr = dict()

    # dampened probability of skipping (1 - d) / N
    skip_chance = (1 - damping_factor) * base_page_rank

    # track changes across PageRank iterations
    significant_changes = 1

    while significant_changes:
        significant_changes = 0
        # build next set of PageRanks
        for page in pages:
            # PR(p) = (1 - d) / N + d * (sum_for_all_i's:(PR(i) / NumLinks(i))
            new_pr[page] = skip_chance + \
                           damping_factor * \
                           sum_for_incoming(page, pages, corpus, page_ranks)

            # was update significant?
            if abs(new_pr[page] - page_ranks[page]) > 0.001:
                significant_changes += 1

        # update to new PageRanks
        page_ranks = new_pr

    return page_ranks


def sum_for_incoming(page, pages, corpus, page_ranks):
    """
    Calculates PR(i) / NumLinks(i) for all incoming link pages and
    returns their sum.

    """
    sum_of_incoming = 0

    for other_page in pages:
        # incoming must be different page
        if other_page == page:
            continue

        # check other page has links
        if corpus[other_page]:
            # check links to current page
            if page in corpus[other_page]:
                # add PR(i) / NumLinks(i) to total
                sum_of_incoming += page_ranks[other_page] / len(corpus[other_page])
        else:
            # if no links, assume a link to every page
            sum_of_incoming += page_ranks[other_page] / len(corpus)

    return sum_of_incoming


if __name__ == "__main__":
    main()
