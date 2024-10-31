import requests
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
from zhipuai import ZhipuAI

# 初始化智谱AI客户端
client = ZhipuAI(api_key="5970c032a7158d0f72d69890e806c912.KOAJqVp6cvhp7LS3")

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-large", torch_dtype=torch_dtype, trust_remote_code=True).to(device)
processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large", trust_remote_code=True)

img_path = "IMG_8669.jpeg"
image = Image.open(img_path)
image = image.convert('RGB')

def run_example(image, task_prompt, text_input=''):
    # Florence 模型处理部分
    prompt = task_prompt + text_input
    inputs = processor(text=prompt, images=image, return_tensors="pt").to(device, torch_dtype)
    
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=1024,
        num_beams=3,
        do_sample=False
    )
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
    parsed_answer = processor.post_process_generation(generated_text, task=task_prompt,
                                                    image_size=(image.width, image.height))
    return parsed_answer

def zhipu_analyze(text):
    """使用新版智谱AI API分析文本"""
    response = client.chat.completions.create(
        model="glm-4",  # 使用GLM-4模型
        messages=[
            {"role": "system", "content": "你是一个专业的图像描述分析助手，请对提供的图片描述进行中文翻译和关键词的提取"},
            {"role": "user", "content": f"请对以下图片描述进行中文翻译和关键词的提取,请你仅返回关键词列表，返回格式为[关键词1,关键词2,关键词3...]：{text}"}
        ]
    )
    # 获取完整的响应内容
    return response.choices[0].message.content

# 获取Florence的描述并用智谱AI进行增强
# florence_basic = run_example(image, task_prompt='<CAPTION>')
# florence_detailed = run_example(image, task_prompt='<DETAILED_CAPTION>')
florence_more_detailed = run_example(image, task_prompt='<MORE_DETAILED_CAPTION>')

# print("Florence简单描述:" + str(florence_basic))
# print("智谱AI增强后的简单描述:" + str(zhipu_analyze(florence_basic)))
# print("\nFlorence细节描述:" + str(florence_detailed))
# print("智谱AI增强后的细节描述:" + str(zhipu_analyze(florence_detailed)))
print("\nFlorence更加具体的描述:" + str(florence_more_detailed))
print("智谱AI增强后的具体描述:" + str(zhipu_analyze(florence_more_detailed)))