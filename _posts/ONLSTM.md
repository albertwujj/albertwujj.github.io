#ICLR Best Paper - Ordered Neuron LSTMs 

Ordered Neuron LSTMs are the invention of the ICLR 2019 submission [Ordered Neurons: Integrating Tree Structures into Recurrent Neural Networks](https://arxiv.org/pdf/1810.09536.pdf), which earned the authors the best paper award. 

The concept of 'Ordered Neurons' is a contribution to the recent efforts to build hierarchical, tree-like structure into recurrent neural networks, through priors or direct supervision. Natural language is naturally structured, with phrases making up clauses, and clauses making up sentences, and so on. A hierarchical structure may also help improve the ability to model long-term dependencies. However, the technique introduced in this paper is especially elegant, introducing only inductive bias and augmenting LSTMs aptly.
How ON-LSTM hopes to capture tree-structured infoNow, natural language has a variety of different tree-shaped decompositions. Let's take an arbitrary example of sentence->clause->phrase.

At each time step, the cell state of the ON-LSTM hopes to capture information for the current token, xt, in addition to all of it's parents in the hierarchical tree structure, which in our example would be the phrase, clause, and sentence xt is contained in. The higher-level nodes may be only partially complete.


This is the intuition. It is incorporated into the standard LSTM cell through the addition of a couple gates, and a new activation function called cumax.
The new activation function cumax is just the cumulative sum of softmax, across the feature dimension. Each output will be a monotonically increasing vector, in the range (0,1). However, the idea behind cumax is to model the expectation of a binary vector of the form [000….111], with some number of 0s, followed by 1s filling out the rest. Cumax is chosen because it is easily differentiable. 
I assume familiarity with the LSTM gates. LSTM gates include a forget gate t which models how much of each element to forget from the previous c state, and an input gate i, which models how much new info to incorporate into the c state. 


Ordered Neuron LSTMs (ON-LSTMs) add two new, 'master' forget and input gates. The forget gate