# from vllm import LLM, SamplingParams
# llm = LLM(model="", memory_utilization=0.9)
# sampling_params = SamplingParams(temperature=0.6, top_p=0.95, max_tokens=128)
# outputs = llm.generate(inputs, sampling_params)

import torch
from pydantic import BaseModel
import psutil

# OHH - we need to implement simple model and attention operation first
# and test everything on CPU

# lets do everything for this model: `meta-llama/Llama-3.2-1B`
# it would be easy to debug on CPU

# TODO: we will support vLLM on CPU as well!!!
# that will make debugging much as easy as I don't have infinite money for GPUs

# later, we need to implement distributed inference with tensor_parallel_size
# and with pipeline_parallel_size eventually

# ohh, lets use flash attention kernel with kv cache for now
# we will write our own flash attenton kernel in triton later
# (lol only flash-1 ; flash-2,3 are super hard)
# we can implement memory efficient attention for infernce on CPU?
# that should be easy to do - YEs! we don't need backward pass as long as we plan to do only inference
# TODO: lets implement CPU only library then first - switching to CUDA should be easy later

# q: (batch_size, 1)
# q: (batch_size, 1, hidden_size)

# k, v: (batch_size, seqlen, hidden_size)

# k_cache, v_cache: (num_blocks, block_size, hidden_size)
# block_table: (batch_size, max_num_blocks)

# lookup of block_table in k_cache/v_cache is (batch_size, max_num_blocks, block_size, hidden_size)
# ~ (batch_size, max_tokens_per_seq, hidden_size)

def flash_attn_with_kvcache(q, k_cache, v_cache, block_table, cache_seqlens):
    # q: (batch_size, 1, num_heads, head_dim)
    # k_cache, v_cache: (num_blocks, block_size, num_kv_heads, head_dim)
    # block_table: (batch_size, max_num_blocks_per_seq)
    # cache_seqlens: (batch_size,)
    return 


# TODO
# we need to implement some family of model?
# can we use huggingface model directly? but KV-cache logic needs to be supported?
# we will prioritise huggingface model implementation if thats possible
# if not, we want to go with deepseek like architecture? but model is too big there for debugging

# lets keep external API as close as possible to vLLM

# llm.generate will consume inputs which is basically list of string
# it will consume all strings and do auto-scheduling and auto-batching

# kv cache is a tensor of shape: (num_blocks, block_size) and occupies memory on hardware
# then there is block_manager which is pointer to memory but has similar schema as kv cache

# whenever a string is passed into generate (note: chat_template needs to passed by user beforehand)
# its tokenized into tokens using tokenizer - basically, list of int
# we make blocks from that list of int (each block is of size 256)

# blocks (CPU) = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# 0-255: block-0 on hardware
# 256-511: block-1 on hardware
# ...

# how are you doing today ?
# 1 2 3 4 5 6 :: sequence of tokens
# [1 2 3 4] [5 6] :: sequence of tokens divided into blocks
# [2] [8] :: sequence of blocks

# we store list of all the blocks (block ID in CPU memory & actual block on hardware)
# we now need to fetch whatever blocks are free

# we need to implement following:
# prompt sharing
# KV cache: (num_blocks, block_size)

# everything, except attention operation, can be computed at token level
# attention operation

# k_block = 

# q_like_tensor = value_compute_with_online_softmax(q@k_block, v_block)
# 

# class BlockManager:
#     def __init__(self):
#         self.free_blocks = 

class SamplingParams(BaseModel):
    temperature: float = 0.6
    top_p: float = 0.95
    max_tokens: int = 128


class LLM:
    def __init__(
        self,
        model,
        tokenizer,
        memory_utilization=0.9,
        device=None,
        block_size=256,
    ):
        self.model = model
        self.tokenizer = tokenizer

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        assert device in {"cuda", "cpu"}

        hidden_size = model.config.hidden_size
        dtype = getattr(torch, model.config.dtype) if device == "cuda" else torch.float32

        if device == "cuda":
            free_memory, total_memory = torch.cuda.mem_get_info()
        else:
            mem_info = psutil.virtual_memory()
            free_memory, total_memory = mem_info.available, mem_info.total

        memory_consumed = total_memory - free_memory
        memory_available = memory_utilization * total_memory - memory_consumed

        block_size_in_bytes = block_size * hidden_size * dtype.itemsize * 2

        num_blocks = memory_available // block_size_in_bytes
        self.kv_cache = torch.empty(num_blocks, block_size, dtype=dtype, device=device)

        self.waiting = []
        self.running = []

    def generate(self, inputs):

        for string in inputs:
            input_ids = self.tokenizer(string, add_special_tokens=False)
            self.waiting.append(input_ids)
        
        
        
        return 
