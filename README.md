

## Finetune QuickStart

```ps
conda create -n internvl python=3.9 --y
pip install -r requirements.txt
```

> 按照InternVL里的安装，微调可能出现报错：
>
> ```
> ================================================ERROR=====================================
> CUDA SETUP: CUDA detection failed! Possible reasons:
> 1. You need to manually override the PyTorch CUDA version. Please see: "https://github.com/TimDettmers/bitsandbytes/blob/main/how_to_use_nonpytorch_cuda.md
> 2. CUDA driver not installed
> 3. CUDA not installed
> 4. You have multiple conflicting CUDA libraries
> 5. Required library not pre-compiled for this bitsandbytes release!
> CUDA SETUP: If you compiled from source, try again with `make CUDA_VERSION=DETECTED_CUDA_VERSION` for example, `make CUDA_VERSION=113`.
> CUDA SETUP: The CUDA version for the compile might depend on your conda install. Inspect CUDA version via `conda list | grep cuda`.
> ```
>
> 解决方案：https://blog.csdn.net/qq_36936730/article/details/132306503
>
> 再次运行可能出现报错：
>
> ```
> from transformers.models.llama.modeling_llama import (LLAMA_ATTENTION_CLASSES,
> ImportError: cannot import name 'LLAMA_ATTENTION_CLASSES' from 'transformers.models.llama.modeling_llama' (/home/pika/App/miniconda3/envs/internvl/lib/python3.9/site-packages/transformers/models/llama/modeling_llama.py)
> ```
>
> 解决方案：
>
> ```
> pip install transformers==4.46.0
> ```
>
> 其余报错缺啥装啥

修改路径：internvl_chat/shell/data/xhs.json

```json
{
    "xhs": {
      "root": [本地images文件夹的上层目录],
      "annotation": [对话文件],
      "data_augment": false,
      "repeat_time": 1,
      "length": 1223
    }
  }
```

```ps
cd InternVL/internvl_chat
GPUS=1 PER_DEVICE_BATCH_SIZE=1 sh shell/internvl2.5/2nd_finetune/internvl2_5_1b_dynamic_res_2nd_finetune_lora.sh
```





