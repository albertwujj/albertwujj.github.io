---
layout: page
title: 'In-Depth: Explaining OpenAI’s GPT-2' 
permalink: /gpt2sampling/
---

In early 2019, OpenAI’s GPT-2 made waves in the media with its ability to produce paragraphs of realistic text, and spawned a controversy due to the decision to withhold the full model.

However, OpenAI did release a smaller, 117M parameter model, complete with code to reproduce it. Strangely, despite having released the code, an explanation how GPT-2 responds to prompts is lacking. In the [GPT-2 paper](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf), the authors’ description of their model is limited to the following:

> We use a Transformer (Vaswani et al., 2017) based architecture for our LMs. The model largely follows the details of the OpenAI GPT model (Radford et al., 2018) with a few modifications.

While the [first GPT paper](https://s3-us-west-2.amazonaws.com/openai-assets/research-covers/language-unsupervised/language_understanding_paper.pdf) does explain the model with a bit more technical depth, their description is still lacking in detail, instead relying on terms from the original Transformer paper without explicitly specifying their constructions.

Furthermore, there is no explanation of the rather interesting way OpenAI adapted their original model to the prompt-based text generation task that made GPT-2 so notorious. The only way I found is the unnecessarily laborious task of reading their undocumented code. However, I have done so, and will provide the explanation. This article will describe the adaptations made for the text-generation task.

The GPT model is based on the decoder part of the [Transformer architecture](https://arxiv.org/pdf/1706.03762.pdf). If you are familiar with the Transformer architecture, go ahead and skim or skip the next four paragraphs. If not, I recommend reading up on it, but will provide a brief, high-level description here.

The Transformer architecture is based off the concept of attention. To explain it briefly, assume we have an input sequence of length M, and we want to produce an output sequence of length N. Using attention, the value at each position y in the output is a combination of every single value in the input. Thus, each position y has M different contributions to its value. However, these M contributions are weighted by a set of M weights, and this set of weights differs for each y.

These weights are calculated as a function of a query and the keys. The query is an item (generally a vector) corresponding to a single position y in the output sequence. In the case of self-attention, the input and output sequences are the same length, and the query is the element in the corresponding position in the input sequence. The keys correspond to the elements in the input sequence, and are usually the elements themselves. One formulation for the weights is simply the dot products of the query with each key. And, yes, in the case of self-attention the queries, keys, and values are simply the elements in the input sequence. This terminology — queries, keys, and values — will be important from here on.

In most applications of attention, each value in both the input and the output sequences are ‘word embeddings’, or a vector that represents a word. If you are unfamiliar with this natural language processing term, I recommend looking it up. A clarification: in this context the ‘word embedding’ will not necessarily be the embedding for a specific real word — rather, you can measure the ‘similarity’ of the embedding to a specific word by taking the dot product of the embedding with the specific word’s actual embedding.

There are two more concepts from the original Transformer paper that help describe the GPT model, which I will go over very briefly. One is multi-head attention. Using a fully-connected layer, the queries, keys, and values are projected to multiple spaces, then the attention result from each space is merged using another fully-connected layer. The second concept is masked attention, where for each position in the output, values corresponding to earlier positions in the input are masked and do not contribute to the result.

OpenAI’s GPT only uses the ‘decoder’ part from the Transformer architecture. Thus, it relies on only self-attention. The ‘decoder’ is composed of multiple decoder layers, each with same-length input and output sequences. Each decoder layer performs multi-headed masked self-attention on the previous layer’s outputs. However, before outputting, the layer puts the results of the self-attention through a fully-connected (e.g. feed forward) layer, where the same fully-connected layer is applied to each element in the sequence.

![](https://cdn-images-1.medium.com/max/1600/1*Ji79bZ3KqpMAjZ9Txv4q8Q.png)The GPT architecture, from the GPT paper

Ultimately, the input to the decoder is a sequence of word embeddings, and the output from the decoder is also a sequence of word embeddings. To those unfamiliar with natural language processing, this may seem like a model for supervised learning. How did OpenAI adapt it to the task of conditional text generation?

The decoder is first trained in an unsupervised manner using a standard language modelling objective. Specifically, our gradient descent loss is a measure of the difference between the input word embeddings and the output word embeddings. Really. Why doesn’t the decoder simply leave its input unchanged to minimize the loss? Since we are using masked self-attention, within each attention operation in the decoder layers, the function for a specific position of the output does not have access to the corresponding input position — only those before. Thus, the decoder is essentially trained to predict the next word of the sequence given all previous words, for each word in the sequence.

We can make use of the final word embedding of the decoder’s output sequence. In the original GPT paper, the supervised fine-tuning section describes passing the final embedding through a fully-connected softmax layer, to then train with gradient descent on any classification task.

For GPT-2’s text generation task, each pass through the whole decoder produces a single word, sampled using the final word embedding. Thus, generated text of 100 words requires 100 passes through the decoder. The input to each pass is a sequence of length 1 containing the embedding for the single sampled word from the previous pass. Correspondingly, the inputs and outputs to the decoder layers within each pass are a sequence of length 1.

Now, you may be rightfully asking: where does attention come into play, if the sequence is of length 1? Attention output at a specific position is a linear combination of the values, weighted by a function of the query for that position and the keys. Using standard self-attention, the queries, keys, and values would each contain only the single input element. In OpenAI’s GPT-2 model, the authors keep track of all the past keys and values from each layer in each of the previous passes.

This is GPT-2’s key algorithmic adaptation. Each layer in each pass has a specific key and value, from its length-1 input sequence. The layer then concatenates this new key to the sequence of all keys from previous passes, and similarly concatenates the values. To give an example, if we are on the 3rd pass through a decoder of 5 layers, our concatenated key sequence will be length 2 * 5 + 1 = 11\. Importantly, in order to ensure the key/value sequences within a single pass are the same length, we concatenate only with keys/values from previous passes, not from previous layers within the current pass.

Now, GPT-2’s famous ability of responding to a prompt is simple. First, the sequence of word embeddings representing the entire prompt is passed through the entire decoder once. The (sampled) final word embedding output is used in the length-1 input sequence to another pass. Subsequent passes, as described above, have input and output sequences of length one. The key/value sequences from the initial pass, which are the length of the prompt, are also concatenated to the keys and values for all future passes. GPT-2’s full response is simply the concatenation of the one-word samples from each pass.

Above, I’ve explained the adaptations made to the Transformer-based GPT model to allow GPT-2 to respond to prompts. I hope you found this essay helpful. Feel free to leave feedback, or let me know if you’d appreciate another post walking through the GPT-2 code in-depth.
