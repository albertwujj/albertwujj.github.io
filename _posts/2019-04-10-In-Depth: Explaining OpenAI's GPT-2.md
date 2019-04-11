---
layout: page
title:  'In-Depth: Explaining OpenAI’s GPT-2'
permalink: /gpt2sampling/
---

In early 2019, OpenAI’s GPT-2 made waves in the media with its ability to produce paragraphs of realistic text, and spawned a controversy due to the decision to withhold the full model.

However, OpenAI did release a smaller, 117M parameter model, complete with code to reproduce it. Strangely, despite having released the code, an explanation how GPT-2 responds to prompts is lacking. In the [GPT-2 paper](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf), the authors’ description of their model is limited to the following:

> We use a Transformer (Vaswani et al., 2017) based architecture for our LMs. The model largely follows the details of the OpenAI GPT model (Radford et al., 2018) with a few modifications.

While the [first GPT paper](https://s3-us-west-2.amazonaws.com/openai-assets/research-covers/language-unsupervised/language_understanding_paper.pdf) does explain the model with a bit more technical depth, their description is still lacking in detail, instead relying on terms from the original Transformer paper without explicitly specifying their constructions.

Furthermore, there is no explanation of the rather interesting way OpenAI adapted their original model to the prompt-based text generation task that made GPT-2 so notorious. The only way I found is the rather laborious task of reading the undocumented code. However, I have done so, and will provide the explanation. This article will describe the adaptations made for the text-generation task.

The GPT model is based on the decoder part of the [Transformer architecture](https://arxiv.org/pdf/1706.03762.pdf). If you are familiar with the Transformer architecture, go ahead and skim or skip the next five paragraphs. If not, I recommend reading up on it, but will provide a brief, high-level description here.

Attention is a concept that includes different operations with certain key similarities. To explain it briefly, assume we have an input sequence of length M. Our attention operation will produce an output sequence of length N. These are both sequences of vectors. In natural language processing, one vector represents one word. Each vector in the output is a unique weighted average of the vectors in the input. Thus, we will need a weight for each (input position, output position) pair.

In order to calculate the weights, ‘Attention’ operations use a set of vectors corresponding to the input sequence, and a set of vectors corresponding to the output sequence. Let’s call these sets keys and queries, respectively.

Then, to determine the weight for a specific (input position, output position) pair, we use the corresponding (key, query) pair. This can be as simple as taking the dot product of the key and query.

So, ‘attention’ covers the broad range of methods based on taking a combination of the input items weighted using ‘keys’ and ‘queries’. Where do we get these keys and queries? In the case of self-attention, where the output sequence is the same size as the input sequence, the keys and queries are both the input sequence itself. If you only use the dot product to calculate weights, each output vector will essentially be the average of the vectors most similar to the corresponding input vector. The self-attention operation will not change the sequence by much at all.

However, there are a couple important modifications which, among other things, helps this issue. One is called multi-head attention. In multi-head attention, the input sequence, queries, and keys are projected to multiple fewer-dimension spaces using a fully-connected neural network layer. Then, the results from the attention operation in each space are concatenated then projected back to the original dimensions using another fully-connected layer.

As the neural-network layers will be trained through gradient descent (our attention operation is differentiable), even if you simply use the dot product to calculate weights within each projected space, the model can learn projections that result in more than just naked similarity between the original key and query.

The second concept is masked self-attention, where for each position in the output, values from earlier positions in the input are masked and do not contribute to the result.

OpenAI’s GPT only uses the ‘decoder’ from the Transformer architecture, relying only on self-attention. The ‘decoder’ is composed of multiple layers, each with the same length input/output sequences. A single decoder layer contains a multi-headed masked self-attention operation and then a fully-connected layer. The fully-connected layer is applied individually to each vector in the sequence.

![](https://cdn-images-1.medium.com/max/1600/1*Ji79bZ3KqpMAjZ9Txv4q8Q.png)The GPT architecture, from the GPT paper

Now, to the actual use of the model. We specified that each element in the input/output sequences is a vector representing a word. The proper natural language processing terminology for this vector is ‘a word embedding’. This is a good topic to read about if you are unfamiliar. To clarify, however — besides in the initial input sequence, each vector is not the exact embedding for a specific word. Rather, you can measure the vector's similarity to specific word embeddings. You can then sample a specific word based on the similarities.

So, the decoder takes a sequence of word embeddings as input, and produces a sequence of word embeddings as output. You can then use sampling techniques to transform the embedding sequence into actual text outputs. But how is the model trained?

The decoder is first trained in an unsupervised manner using a standard language modelling objective. Specifically, the loss we minimize is (a measure of) the difference between the input word embeddings and the output word embeddings. Really. Why doesn’t the decoder simply leave its input unchanged to minimize the loss? Since we are using masked self-attention, the weighted average for an output vector will only contain the input vectors corresponding to previous positions. Thus the attention operation cannot simply copy the matching position. The decoder essentially is trained to predict the next word of the sequence given all previous words, for each word in the sequence.

We can creatively use the final word embedding of the decoder’s output sequence. In the original GPT paper, the supervised fine-tuning section describes passing the final embedding through a fully-connected softmax layer in order to perform any text classification task.

However, GPT-2’s pièce de résistance is its ability to generate responses to prompts. Indeed, reading only popular articles that would seem like its only ability. Given what we know of the actual model, how does it work?

GPT-2 generates its responses word by word, each individual word sampled from the final output embedding of a pass through the entire decoder. The input to each pass is a sequence of length 1 containing the embedding of the previously produced word. Correspondingly, the sequences within each decoder layer are length 1.

Now, you may be rightfully asking: where does attention come into play, if the sequences are of length 1?

This is GPT-2’s key algorithmic adaptation. GPT-2 keeps track of the past keys and corresponding input vectors, from each decoder layer in each of the previous passes. Each decoder layer has a new key and corresponding input vector, namely the vector in its length-1 input sequence. Let’s call the key’s corresponding input vector the ‘value’, although the key and value are the same vector in the case of self-attention. The decoder layer then concatenates this new key/value to the end of the keys/values from previous passes, which are kept in order.

To give an example, if we are on the 3rd pass through a decoder of 5 layers, our concatenated key/value sequence will be length 2 * 5 + 1 = 11\. Importantly, in order to ensure the key/value sequences within a single pass are the same length, we only concatenate with keys/values from previous passes, not from previous layers within the current pass.

Now, the famous ability of responding to a prompt is simple. First, the prompt is converted to a sequence of word embeddings, which is passed through the decoder once, producing a sequence of output embeddings. The first generated word is sampled from the final embedding.

The embedding for the generated word is then used as the length-1 input sequence to another pass. This pass produces a single embedding, from which another word is sampled. And thus the process repeats, adding a single word to GPT-2’s response with each pass.

Above, I have explained the adaptations made to the Transformer-based GPT model to allow GPT-2 to respond to prompts. I hope you found this essay helpful. Feel free to leave feedback, or let me know if you’d appreciate another post walking through the GPT-2 code in-depth.

