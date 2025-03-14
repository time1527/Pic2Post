import os
import json

HEADER_PROMPT = """
你是一名资深小红书运营专家，擅长小红书文案撰写。
你需要根据主题，生成10个不同的小红书标题。按行式输出，每行一个标题。不需要标号。
主题：
{subject}
标题：
"""

FLUX_PROMPT = """
你是一名资深小红书运营专家，擅长用英文生成图片prompt。根据标题生成1-9个不同的flux图片描述，需包含场景、元素、风格细节，格式如下：

### 规则
1. **prompt 结构**（英文）：
   - **场景**：主场景描述（如咖啡馆、雪山、节日街道）
   - **元素**：核心物体/人物+动作+位置（如“女孩手捧书坐在窗边”）
   - **细节**：颜色/材质/光影（如“暖光照射的木质纹理”）
   - **风格**：摄影或艺术风格（如“胶片摄影/3D插画/极简平面”）

2. **参数要求**：
   - `width` 和 `height` 必须为具体数值：
     - 竖版: 768x1024
     - 方版: 1024x1024
     - 横版: 1024x768

### 示例（已转义大括号）：
```json
{{
    "prompts": [
        {{
            "prompt": "Cozy bookstore interior scene, wooden shelves filled with books, a cup of coffee on a round table by the window, warm golden hour lighting, vintage filter style",
            "width": "768",
            "height": "1024"
        }},
        {{
            "prompt": "Minimalist flat design of summer beach, abstract waves pattern in turquoise and white, coconut tree silhouette, geometric shape composition, pastel color palette",
            "width": "1080",
            "height": "1080"
        }}
    ]
}}
标题：
{header}
你生成的flux prompts（英文JSON）：
"""

COT_PROMPT = """
你是一名视觉智能体，请基于标题和图片内容按以下架构处理小红书文案生成，假设你看到的是图片，而不是图片prompt。在思考的过程中，也不要提及prompt：
<think>
...
</think>
<answer>
...
</answer>


标题：{header}
图片prompt：{prompt}
你生成的小红书文案：
"""

WO_IMAGE_PROMPT = """
你是一名小红书运营，精通小红书文案撰写，请基于标题按以下架构生成小红书文案：
<think>
...
</think>
<answer>
...
</answer>
标题：{header}
你生成的小红书文案：
"""

virtual_system = """根据以下格式回答问题:
<think>
...
</think>
<answer>
...
</answer>
"""
prompts = [
    """根据{header}生成一篇适合小红书的文案，要求内容生动有趣，能够吸引读者阅读，并带有实用的干货信息！""",
    """请围绕{header}写一篇小红书风格的笔记，语言轻松自然，代入感强，能够引起用户的共鸣，适合点赞收藏！""",
    """围绕{header}撰写一篇小红书种草文案，内容真实有趣，可结合个人体验或推荐理由，让用户有尝试的欲望！""",
    """请根据{header}创作一篇小红书风格的内容，要求具备吸引力，可以用幽默、情感或故事化的方式呈现！""",
    """基于{header}写一篇小红书分享笔记，内容要有温度感，像朋友聊天一样轻松自然，并且带有实用价值！""",
    """围绕{header}撰写一篇适合小红书的文案，要求内容生动形象，能够让用户产生共鸣，并有实际的参考价值！""",
    """请根据{header}写一篇小红书笔记，要求内容真实，风格轻松，适合用户分享和种草，可加入实用的小贴士！""",
    """围绕{header}生成一篇小红书风格的种草文案，内容需要结合真实体验，表达对产品或体验的真实感受！""",
    """请基于{header}写一篇小红书风格的推荐文案，要求文案轻松自然，不要过于生硬推销，要有代入感！""",
    """根据{header}创作一篇适合小红书的内容，文案需要具备社交属性，让读者愿意转发、点赞或留言互动！""",
    """请围绕{header}撰写一篇小红书风格的种草笔记，要求内容生动具体，最好结合真实经历或使用感受！""",
    """基于{header}写一篇适合小红书的分享文案，内容需要有趣、有吸引力，同时具备实用性，让人愿意收藏！""",
    """请根据{header}写一篇符合小红书风格的笔记，要求内容易读易懂，富有情感和共鸣感，适合社交传播！""",
    """围绕{header}撰写一篇小红书推荐文案，要求结合真实体验，带有强烈的代入感，并配有实用的小贴士！""",
    """请基于{header}生成一篇小红书风格的笔记，文案需要有趣味性，同时具备实用价值，让用户愿意互动！""",
    """根据{header}写一篇小红书风格的种草文案，要求内容真实可信，不要太过广告化，而是以体验为主！""",
    """围绕{header}创作一篇符合小红书风格的分享文案，文案要有代入感，吸引用户点赞、收藏和关注！""",
    """请基于{header}写一篇小红书推荐文案，内容需要结合个人体验或用户反馈，让推荐更加有说服力！""",
    """根据{header}撰写一篇小红书风格的内容，要求语言生动，富有感染力，让读者有强烈的尝试欲望！""",
    """围绕{header}写一篇小红书种草笔记，内容可以结合真实使用感受，并加入互动式问题，引导评论！""",
    """请基于{header}创作一篇小红书风格的文案，要求内容轻松自然，可以带点幽默感，让人容易接受！""",
    """根据{header}撰写一篇符合小红书风格的种草文案，内容生动有趣，可结合实际使用场景进行描述！""",
    """请围绕{header}写一篇小红书分享笔记，要求内容有吸引力，并能够引起用户共鸣，适合点赞收藏！""",
    """基于{header}写一篇小红书风格的文案，要求结合实际体验或真实测评，让内容更加真实有说服力！""",
    """请根据{header}生成一篇符合小红书风格的推荐笔记，要求文案富有感染力，并能引导用户互动！""",
    """围绕{header}撰写一篇小红书风格的内容，要求文案有吸引力，并配有实用的小技巧或推荐理由！""",
    """请基于{header}写一篇小红书种草文案，要求内容真实自然，避免生硬推销，适合社交平台传播！""",
    """根据{header}写一篇适合小红书的分享文案，要求结合真实体验，并且语言风格亲切自然，适合互动！""",
    """请围绕{header}撰写一篇符合小红书风格的种草笔记，内容生动形象，适合点赞、收藏和分享！""",
    """基于{header}生成一篇小红书风格的推荐文案，内容需真实可信，并带有情感共鸣，增强吸引力！""",
    """请根据{header}写一篇小红书风格的内容，文案需要有感染力，并能让用户有尝试或购买的冲动！""",
    """围绕{header}创作一篇小红书种草文案，要求内容轻松有趣，可以加入真实测评或个人使用体验！""",
    """请基于{header}写一篇小红书风格的推荐笔记，文案需生动形象，并结合具体使用场景来提升说服力！""",
    """根据{header}撰写一篇符合小红书风格的分享文案，要求语言自然轻松，能够引导用户参与互动！""",
    """请围绕{header}写一篇小红书风格的内容，要求文案富有吸引力，并且适合在社交媒体上传播！""",
    """根据{header}生成一篇小红书文案，内容生动有趣，搭配图片增强吸引力，让读者有代入感！""",
    """围绕{header}撰写一篇适合小红书的笔记，语言轻松自然，结合图片增加互动感！""",
    """结合{header}创作一篇小红书风格的分享文案，内容真实有代入感，适合点赞收藏！""",
    """根据{header}撰写一篇适合小红书的内容，要求文案有吸引力，配图增强氛围感！""",
    """围绕{header}创作一篇小红书分享文案，图文结合，增强社交传播属性！""",
    """基于{header}撰写一篇小红书笔记，内容轻松自然，配图能够吸引用户注意！""",
    """围绕{header}生成一篇适合小红书的文案，图片辅助展示，增强互动性！""",
    """针对{header}写一篇小红书种草文案，内容真实，搭配图片展示细节！""",
    """围绕{header}创作一篇小红书风格的分享文案，增强读者互动感！""",
    """基于{header}撰写小红书内容，结合真实体验，图片与文字互相补充！""",
    """围绕{header}写一篇小红书风格的笔记，文案有吸引力，图片辅助增强感染力！""",
    """围绕{header}撰写小红书内容，结合图片讲述使用体验，让笔记更生动！""",
    """基于{header}写一篇小红书种草文案，语言轻松，图片生动，提高分享率！""",
    """围绕{header}创作小红书笔记，内容有趣，图片帮助传达更多细节！""",
    """围绕{header}写一篇适合小红书的分享笔记，配图增加吸引力！""",
    """围绕{header}撰写小红书笔记，内容有趣有料，配合图片提升互动体验！""",
    """围绕{header}创作小红书内容，配图与文字互相补充，增强阅读体验！""",
    """根据{header}创作一篇小红书笔记，图文结合，增强代入感，让用户更愿意阅读和分享！""",
    """围绕{header}生成一篇适合小红书的文案，内容有趣易懂，配图提升吸引力，让人忍不住点赞！""",
    """写一篇关于{header}的种草笔记，结合图片让内容更直观，吸引用户参与互动！""",
    """生成一篇小红书风格的分享文案，围绕{header}展开，图文结合，提高可读性和传播度！""",
    """撰写关于{header}的体验分享，内容真实有代入感，搭配图片增强信服力！""",
    """针对{header}创作一篇小红书推荐笔记，文字轻松自然，配合图片优化视觉效果！""",
    """写一篇关于{header}的种草文案，结合高质量图片，提升用户信赖感和兴趣！""",
    """围绕{header}生成一篇适合小红书的文案，要求图文并茂，增强互动性，提高用户转化率！""",
    """创建一篇小红书笔记，围绕{header}展开，搭配图片吸引用户注意，让内容更具吸引力！""",
    """基于{header}撰写小红书风格的内容，要求语言轻松自然，结合图片提升互动效果！""",
    """围绕{header}创作小红书推荐文案，结合真实体验，配合图片提升说服力！""",
    """生成一篇关于{header}的测评笔记，图文结合，真实生动，让读者更有代入感！""",
    """撰写一篇围绕{header}的小红书文案，图文搭配，提升可读性，让用户愿意收藏！""",
    """创建一篇关于{header}的小红书内容，结合图片展示细节，让推荐更具说服力！""",
    """围绕{header}撰写一篇小红书分享文案，结合图片让内容更具表现力和感染力！""",
    """生成一篇适合小红书的种草内容，围绕{header}展开，图文结合，增强用户互动感！""",
    """撰写一篇关于{header}的推荐笔记，结合图片展示细节，提高用户对内容的信赖感！""",
    """创作一篇围绕{header}的真实测评文案，结合图片增强可读性，让用户更容易理解！""",
    """写一篇围绕{header}的小红书笔记，结合图片，增强视觉吸引力，让内容更具吸引力！""",
    """创建一篇关于{header}的分享文案，内容真实有趣，图文结合，增强互动性！""",
    """撰写一篇适合小红书的种草笔记，以{header}为主题，结合图片提高可读性！""",
    """生成关于{header}的测评文案，结合图片展示实际效果，让推荐更具说服力！""",
    """创作一篇围绕{header}的种草内容，要求文案生动有趣，图文结合，提升用户兴趣！""",
    """围绕{header}撰写小红书推荐笔记，内容真实，结合图片增加可信度！""",
    """写一篇关于{header}的体验分享，搭配图片增强吸引力，让内容更容易传播！""",
    """创建一篇围绕{header}的小红书风格文案，图文结合，让内容更具表现力！""",
    """撰写一篇关于{header}的种草笔记，内容生动形象，结合图片优化视觉呈现！""",
    """生成一篇小红书笔记，主题是{header}，要求图文结合，提升用户体验！""",
    """围绕{header}创作一篇小红书种草文案，结合图片提升吸引力，让用户更容易被种草！""",
    """写一篇关于{header}的测评分享，结合图片增强真实感，让推荐更具说服力！""",
    """创建一篇围绕{header}的内容，要求符合小红书风格，图文结合，提高互动性！""",
    """生成一篇适合小红书的推荐笔记，围绕{header}展开，图文结合，吸引用户注意！""",
    """撰写一篇关于{header}的小红书文案，内容生动，结合图片提升阅读体验！""",
    """创作一篇围绕{header}的真实体验笔记，配合图片展示使用效果！""",
    """写一篇小红书风格的种草笔记，主题是{header}，结合图片提高互动性！""",
    """围绕{header}撰写小红书分享文案，要求图文结合，增强可读性！""",
    """生成一篇关于{header}的测评内容，搭配图片，让用户更直观地了解产品！""",
    """创建一篇适合小红书的内容，围绕{header}展开，结合图片增强吸引力！""",
    """撰写一篇关于{header}的体验分享，结合图片展现细节，提高阅读体验！""",
    """围绕{header}创作一篇小红书风格的笔记，要求图文结合，增强互动性！""",
    """写一篇关于{header}的种草文案，结合高质量图片，提高用户信赖感！""",
    """生成一篇围绕{header}的小红书分享内容，配合图片，让用户更容易被吸引！""",
    """撰写一篇关于{header}的测评笔记，结合图片展示使用体验，提高说服力！""",
    """创建一篇适合小红书的内容，围绕{header}展开，图文结合，增加互动性！""",
    """写一篇关于{header}的小红书文案，内容要真实有趣，图文结合，让读者愿意分享！""",
    """基于{header}撰写一篇小红书笔记，搭配图片提高吸引力，让内容更加生动！""",
    """根据{header}生成一篇小红书文案，要求图文并茂，生动有趣，吸引用户点赞！""",
    """围绕{header}创作一篇小红书文案，搭配实拍图片，增强用户互动性！""",
    """生成一篇关于{header}的小红书种草文案，内容具有可读性，结合图片增强说服力！""",
    """撰写一篇围绕{header}的小红书风格内容，结合图片，提升用户对产品的兴趣！""",
    """基于{header}写一篇小红书笔记，内容轻松自然，图文结合，让读者想要尝试！""",
    """根据{header}创作一篇小红书文案，要求文字幽默，搭配图片增加互动感！""",
    """撰写一篇关于{header}的种草笔记，图文并茂，提升用户的参与度！""",
    """生成一篇围绕{header}的体验分享，结合图片展示效果，提高用户的购买欲！""",
    """写一篇关于{header}的推荐文案，结合图片讲述实际使用体验，让内容更具信服力！""",
    """围绕{header}撰写一篇小红书分享文案，图文结合，增强传播效果！""",
    """创作一篇小红书风格的文案，内容围绕{header}展开，结合图片提升可读性！""",
    """生成一篇关于{header}的推荐文案，图文并茂，增强视觉冲击力！""",
    """写一篇围绕{header}的小红书分享，结合图片增强吸引力，提升用户信任感！""",
    """根据{header}创作小红书内容，要求图文结合，语言生动有趣，让用户感同身受！""",
    """撰写一篇关于{header}的种草笔记，图文结合，提高内容吸引力，让读者想要购买！""",
    """围绕{header}写一篇小红书分享，结合图片，增强用户对内容的兴趣和认同感！""",
    """生成一篇围绕{header}的测评文案，图文结合，增强内容的真实性和吸引力！""",
    """撰写一篇小红书文案，主题是{header}，结合图片提升文章的可读性！""",
    """根据{header}创作一篇分享文案，结合图片，增强互动性，提升用户参与度！""",
    """围绕{header}生成一篇小红书种草笔记，图文结合，增强推荐的可信度！""",
    """生成一篇关于{header}的推荐文案，结合图片展示实际效果，让内容更具说服力！""",
    """写一篇围绕{header}的体验笔记，结合图片对比，提升用户的兴趣！""",
    """创作一篇关于{header}的小红书文案，图文并茂，增强用户的信赖感！""",
    """撰写一篇围绕{header}的小红书分享，要求内容真实，图片增强细节！""",
    """根据{header}创作一篇小红书笔记，内容有趣，搭配图片提升可读性！""",
    """写一篇关于{header}的推荐文案，图文结合，提升推荐的效果和信任感！""",
    """围绕{header}创作一篇分享文案，图文结合，增加传播力，吸引更多读者！""",
    """生成一篇小红书风格的种草笔记，结合图片提高互动性，吸引更多关注！""",
    """撰写一篇关于{header}的测评文案，结合图片展示产品特点，增强说服力！""",
    """围绕{header}生成一篇小红书分享，图文结合，帮助用户更好地了解产品！""",
    """创作一篇关于{header}的推荐内容，结合高质量图片增强信任感和购买欲！""",
    """写一篇围绕{header}的小红书文案，内容简洁明了，图片提升阅读体验！""",
    """生成一篇关于{header}的真实分享文案，图文结合，增强内容的真实感！""",
    """撰写一篇关于{header}的小红书笔记，图文结合，提升阅读的趣味性和吸引力！""",
    """写一篇围绕{header}的种草笔记，内容轻松有趣，配图提高可读性！""",
    """根据{header}生成一篇小红书分享，图文结合，提升内容的互动性和传播效果！""",
    """围绕{header}写一篇小红书文案，要求内容真实，搭配图片提升吸引力！""",
    """生成一篇关于{header}的小红书推荐文案，图文结合，让内容更具感染力！""",
    """撰写一篇围绕{header}的分享文案，结合图片，提升文章的可信度和互动性！""",
    """写一篇关于{header}的小红书文案，结合高质量图片，提升内容的表现力！""",
    """围绕{header}创作一篇小红书种草笔记，图文结合，增强内容的吸引力！""",
    """根据{header}撰写一篇分享内容，结合图片展现效果，提升可读性！""",
    """创作一篇小红书文案，主题是{header}，内容轻松有趣，配图吸引眼球！""",
    """围绕{header}写一篇小红书笔记，要求文字生动有趣，搭配图片提升互动性！""",
    """根据{header}撰写一篇小红书文案，内容真实生动，图片搭配增强吸引力！""",
    """写一篇围绕{header}的小红书种草笔记，图文结合，增强用户对产品的信任感！""",
    """围绕{header}撰写一篇小红书分享，图文结合，增加互动性和参与感！""",
    """生成一篇关于{header}的小红书文案，图文并茂，提升用户阅读兴趣！""",
    """写一篇关于{header}的小红书种草文案，图文结合，提升分享率和参与感！""",
]


def gen_header(subjects_file_path):
    import dashscope

    subjects = []
    with open(subjects_file_path, "r", encoding="utf-8") as file:
        subjects = file.read()

    subjects = subjects.split("\n")
    subjects = [subject for subject in subjects if subject != ""]

    headers = []

    for s in subjects:
        prompt = HEADER_PROMPT.format(subject=s)
        messages = [{"role": "user", "content": prompt}]
        response = dashscope.Generation.call(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="qwen-turbo",  # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=messages,
            result_format="message",
            presence_penalty=1.5,
        )
        headers.extend(
            response["output"]["choices"][0]["message"]["content"].split("\n")
        )
    with open("header.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(headers))


def gen_flux_prompt(headers_file_path, api_key):
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    headers = []
    with open(headers_file_path, "r", encoding="utf-8") as file:
        headers = file.read()

    headers = headers.split("\n")
    headers = [header for header in headers if header != ""]

    cnt = 0
    with open("flux.json", "w", encoding="utf-8") as json_file:
        json_file.write("[\n")  # 开始写入 JSON 数组
        for i, h in enumerate(headers):
            prompt = FLUX_PROMPT.format(header=h)
            messages = [{"role": "user", "content": prompt}]

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                response_format={"type": "json_object"},
            )

            try:
                item = {
                    "id": cnt,
                    "header": h,
                    "flux": json.loads(response.choices[0].message.content),
                }
                json.dump(item, json_file, ensure_ascii=False, indent=4)
                if i < len(headers) - 1:
                    json_file.write(",\n")  # 在每个对象之间添加逗号
                cnt += 1
            except Exception as e:
                print(f"Error processing header '{h}': {e}")
        json_file.write("\n]")  # 结束 JSON 数组


def gen_image(model="flux-schnell"):
    from http import HTTPStatus
    import requests
    from dashscope import ImageSynthesis

    with open("flux.json", "r", encoding="utf-8") as file:
        flux = json.load(file)
        for i, item in enumerate(flux):
            for j, prompt in enumerate(item["flux"]["prompts"]):
                if j > 1:
                    continue
                input_prompt = prompt["prompt"]
                size = prompt["width"] + "*" + prompt["height"]

                rsp = ImageSynthesis.call(
                    model=model, prompt=input_prompt, size=size, seed=42
                )
                if rsp.status_code == HTTPStatus.OK:
                    # print(rsp.output)
                    # print(rsp.usage)
                    # save file to images directory
                    t = item["id"]
                    for result in rsp.output.results:
                        file_name = f"images/{t}_{j}.jpg"
                        with open(file_name, "wb+") as f:
                            f.write(requests.get(result.url).content)
                else:
                    print(
                        "Failed, status_code: %s, code: %s, message: %s"
                        % (rsp.status_code, rsp.code, rsp.message)
                    )


def gen_cot(image_dir, api_key):
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    with open("flux.json", "r", encoding="utf-8") as file:
        flux = json.load(file)
    with open("cot.json", "w", encoding="utf-8") as json_file:
        json_file.write("[\n")  # 开始写入 JSON 数组
        for i, item in enumerate(flux):
            flux_prompts = []
            image_path = []
            for j, prompt in enumerate(item["flux"]["prompts"]):
                t = item["id"]
                if os.path.exists(f"{image_dir}/{t}_{j}.jpg"):
                    flux_prompts.append(prompt["prompt"])
                    image_path.append(f"{image_dir}/{t}_{j}.jpg")
            if len(flux_prompts) == 0:
                prompt = WO_IMAGE_PROMPT.format(header=item["header"])
            else:
                prompt = COT_PROMPT.format(header=item["header"], prompt=flux_prompts)
            messages = [{"role": "user", "content": prompt}]
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
            )
            cot_item = {
                "id": item["id"],
                "header": item["header"],
                "images": image_path,
                "cot": response.choices[0].message.content,
            }
            json.dump(cot_item, json_file, ensure_ascii=False, indent=4)
            if i < len(flux) - 1:
                json_file.write(",\n")  # 在每个对象之间添加逗号
        json_file.write("\n]")  # 结束 JSON 数组


def gen_final():
    data = []
    with open("cot.json", "r", encoding="utf-8") as file:
        cot = json.load(file)
    with open("flux.json", "r", encoding="utf-8") as file:
        flux = json.load(file)

    def find_index(image_path):
        filename = image_path.split("/")[-1]
        index = filename.split("_")[1].split(".")[0]
        return int(index)

    # merge cot and flux
    flux_index = 0
    for i, item in enumerate(cot):
        new_item = {}
        type = "text"
        # id
        new_item["id"] = item["id"]
        # images
        if len(item["images"]) == 1:  # single image
            new_item["image"] = item["images"][0]
            type = "single-image"
        elif len(item["images"]) > 1:  # multi image
            new_item["images"] = item["images"]
            type = "multi-image"

        while flux_index < len(flux) and flux[flux_index]["id"] != item["id"]:
            flux_index += 1
        # width height
        if type == "multi-image":
            assert isinstance(new_item["images"], list)
            new_item["width_list"] = [
                flux[flux_index]["flux"]["prompts"][find_index(t)]["width"]
                for t in new_item["images"]
            ]
            new_item["height_list"] = [
                flux[flux_index]["flux"]["prompts"][find_index(t)]["height"]
                for t in new_item["images"]
            ]
        elif type == "single-image":
            assert isinstance(new_item["image"], str)
            new_item["width"] = flux[flux_index]["flux"]["prompts"][
                find_index(new_item["image"])
            ]["width"]
            new_item["height"] = flux[flux_index]["flux"]["prompts"][
                find_index(new_item["image"])
            ]["height"]
        # conversation
        import random

        prm = random.choice(prompts).format(header="标题“" + item["header"] + "”")
        # https://github.com/OpenGVLab/InternVL/issues/658
        # https://github.com/OpenGVLab/InternVL/issues/654
        if random.randint(0, 1):
            if type == "multi-image":
                prm = "<image>\n<image>\n" + prm
            elif type == "single-image":
                prm = "<image>\n" + prm
        else:
            if type == "multi-image":
                prm = prm + "\n<image>\n<image>"
            elif type == "single-image":
                prm = prm + "\n<image>"

        new_item["conversations"] = [
            {
                "from": "human",
                "value": virtual_system + prm,
            },
            {
                "from": "gpt",
                "value": item["cot"],
            },
        ]
        data.append(new_item)
    with open("output.jsonl", "w", encoding="utf-8") as jsonl_file:
        for item in data:
            jsonl_file.write(json.dumps(item, ensure_ascii=False) + "\n")


def gen_llama_factory():
    data = []
    with open("cot.json", "r", encoding="utf-8") as file:
        cot = json.load(file)
    with open("flux.json", "r", encoding="utf-8") as file:
        flux = json.load(file)

    current_directory = os.path.dirname(os.path.abspath(__file__))
    print(current_directory)
    # merge cot and flux
    flux_index = 0
    for i, item in enumerate(cot):
        new_item = {}
        type = 0
        # images

        new_item["images"] = [
            os.path.join(current_directory, t[2:]) for t in item["images"]
        ]
        type = len(new_item["images"])

        while flux_index < len(flux) and flux[flux_index]["id"] != item["id"]:
            flux_index += 1
        # conversation
        import random

        prm = random.choice(prompts).format(header="标题“" + item["header"] + "”")
        # https://github.com/OpenGVLab/InternVL/issues/658
        # https://github.com/OpenGVLab/InternVL/issues/654
        prm = "<image>\n" * type + prm

        new_item["messages"] = [
            {
                "role": "user",
                "content": virtual_system + prm,
            },
            {
                "role": "assistant",
                "content": item["cot"],
            },
        ]
        data.append(new_item)
    with open("llama_factory.jsonl", "w", encoding="utf-8") as jsonl_file:
        for item in data:
            jsonl_file.write(json.dumps(item, ensure_ascii=False) + "\n")
