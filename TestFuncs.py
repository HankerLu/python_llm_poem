import requests
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
from zhipuai import ZhipuAI

class ImageAnalyzer:
    def __init__(self):
        self.client = None
        self.model = None
        self.processor = None
        self.device = None
        self.torch_dtype = None
        
    def initialize(self):
        """初始化模型和客户端"""
        # 初始化智谱AI客户端
        self.client = ZhipuAI(api_key="5970c032a7158d0f72d69890e806c912.KOAJqVp6cvhp7LS3")
        
        # 设置设备和数据类型
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        # 加载Florence模型
        self.model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Florence-2-large", 
            torch_dtype=self.torch_dtype, 
            trust_remote_code=True
        ).to(self.device)
        
        self.processor = AutoProcessor.from_pretrained(
            "microsoft/Florence-2-large", 
            trust_remote_code=True
        )
        
        return True

    def run_florence(self, image, task_prompt='<MORE_DETAILED_CAPTION>', text_input=''):
        """运行Florence模型进行图像分析"""
        if not all([self.model, self.processor, self.device, self.torch_dtype]):
            raise RuntimeError("模型未初始化，请先调用initialize()")
            
        prompt = task_prompt + text_input
        inputs = self.processor(
            text=prompt, 
            images=image, 
            return_tensors="pt"
        ).to(self.device, self.torch_dtype)
        
        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            num_beams=3,
            do_sample=False
        )
        
        generated_text = self.processor.batch_decode(
            generated_ids, 
            skip_special_tokens=False
        )[0]
        
        parsed_answer = self.processor.post_process_generation(
            generated_text, 
            task=task_prompt,
            image_size=(image.width, image.height)
        )
        return parsed_answer

    def run_zhipu(self, text):
        """运行智谱AI进行关键词提取"""
        if not self.client:
            raise RuntimeError("智谱AI客户端未初始化，请先调用initialize()")
            
        response = self.client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "system", "content": "你是一个专业的图像描述分析助手，请对提供的图片描述进行中文翻译和关键词的提取"},
                {"role": "user", "content": f"请对以下图片描述进行中文翻译和关键词的提取,请你仅返回关键词列表，返回格式为[关键词1,关键词2,关键词3...]：{text}"}
            ]
        )
        return response.choices[0].message.content

    def analyze_image(self, image):
        """完整的图像分析流程"""
        florence_result = self.run_florence(image)
        keywords = self.run_zhipu(florence_result)
        return florence_result, keywords

# 创建全局实例
analyzer = ImageAnalyzer()