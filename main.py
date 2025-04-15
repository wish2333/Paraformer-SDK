# from math import e
from logging import config
import os
import json
import tempfile
from pathlib import Path
import dashscope
from dashscope.audio.asr import Transcription

# from numpy import full
import streamlit as st
import requests
from datetime import timedelta

# 配置文件路径
CONFIG_FILE = "config.json"


# 默认配置
DEFAULT_CONFIG = {
    "api_key": "",
    "model": "paraformer-v2",
    "vocabulary_id": "",
    "phrase_id": "",
    "channel_id": [0],
    "disfluency_removal_enabled": False,
    "timestamp_alignment_enabled": False,
    "special_word_filter": "",
    "diarization_enabled": False,
    "speaker_count": None,
}


# 初始化配置
def init_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f)


# 读取配置
def read_config():
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        # 确保新添加的字段有默认值
        for key in DEFAULT_CONFIG:
            if key not in config:
                config[key] = DEFAULT_CONFIG[key]
        return config


# 保存配置
def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


def get_upload_policy():
    """获取文件上传凭证"""
    try:
        config = read_config()

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }

        params = {"action": "getPolicy", "model": config["model"]}

        response = requests.get(
            "https://dashscope.aliyuncs.com/api/v1/uploads",
            headers=headers,
            params=params,
        )

        if response.status_code == 200:
            return response.json()["data"]
        else:
            st.error(f"获取上传凭证失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"获取上传凭证失败: {str(e)}")
        return None


def upload_file_to_dashscope(file_path):
    """上传文件到临时存储空间并返回URL"""
    try:
        # 获取上传凭证
        policy_data = get_upload_policy()
        if not policy_data:
            return None

        # 准备上传参数
        file_name = Path(file_path).name
        key = f"{policy_data['upload_dir']}/{file_name}"

        files = {"file": open(file_path, "rb")}

        data = {
            "OSSAccessKeyId": policy_data["oss_access_key_id"],
            "policy": policy_data["policy"],
            "Signature": policy_data["signature"],
            "key": key,
            "x-oss-object-acl": policy_data["x_oss_object_acl"],
            "x-oss-forbid-overwrite": policy_data["x_oss_forbid_overwrite"],
            "success_action_status": "200",
        }

        # 上传文件
        response = requests.post(policy_data["upload_host"], files=files, data=data)

        if response.status_code == 200:
            return f"oss://{key}"
        else:
            st.error(f"文件上传失败: {response.text}")
            return None

    except Exception as e:
        st.error(f"文件上传失败: {str(e)}")
        return None
    finally:
        if "file" in locals():
            files["file"].close()


# 语音识别函数
def transcribe_audio(file_url, language_hints):
    config = read_config()
    dashscope.api_key = config["api_key"]

    # 构建请求参数
    params = {
        "model": config["model"],
        "file_urls": [file_url],
        "language_hints": language_hints,
        "vocabulary_id": config["vocabulary_id"] or None,
        "phrase_id": config["phrase_id"] or None,
        "channel_id": config["channel_id"],
        "disfluency_removal_enabled": config["disfluency_removal_enabled"],
        "timestamp_alignment_enabled": config["timestamp_alignment_enabled"],
        "special_word_filter": config["special_word_filter"] or None,
        "diarization_enabled": config["diarization_enabled"],
    }

    # 添加OSS资源解析头
    if file_url.startswith("oss://"):
        params["headers"] = {"X-DashScope-OssResourceResolve": "enable"}

    if config["speaker_count"]:
        params["speaker_count"] = config["speaker_count"]

    with st.spinner("识别中..."):
        task_response = Transcription.async_call(**params)
        if task_response.status_code != 200:
            st.error(f"异步任务创建失败: {task_response.message}")
            return None

        try:
            transcribe_response = Transcription.wait(
                task=task_response.output.task_id,
                timeout=60,  # 设置60秒超时
            )
        except Exception as e:
            st.error(f"任务等待失败: {str(e)}")
            return None

    return (
        transcribe_response.output if transcribe_response.status_code == 200 else None
    )


# Streamlit界面
def main():
    st.title("语音识别SDK")

    # 初始化配置
    init_config()
    config = read_config()

    # API Key和模型设置
    with st.expander("基本设置"):
        api_key = st.text_input("API Key", value=config["api_key"], type="password")
        model = st.selectbox(
            "模型",
            ["paraformer-v2", "paraformer-v1"],
            index=0 if config["model"] == "paraformer-v2" else 1,
        )

    # 高级设置
    with st.expander("高级设置"):
        col1, col2 = st.columns(2)
        with col1:
            vocabulary_id = st.text_input("热词ID(v2)", value=config["vocabulary_id"])
            phrase_id = st.text_input("热词ID(v1)", value=config["phrase_id"])
            channel_id = st.text_input(
                "音轨索引(逗号分隔)", value=",".join(map(str, config["channel_id"]))
            )

        with col2:
            disfluency_removal = st.checkbox(
                "过滤语气词", value=config["disfluency_removal_enabled"]
            )
            timestamp_alignment = st.checkbox(
                "时间戳校准", value=config["timestamp_alignment_enabled"]
            )
            special_word_filter = st.selectbox(
                "敏感词过滤",
                ["", "filter", "replace"],
                index=["", "filter", "replace"].index(config["special_word_filter"]),
            )

    # 说话人分离设置
    with st.expander("说话人分离"):
        diarization_enabled = st.checkbox(
            "启用说话人分离", value=config["diarization_enabled"]
        )
        speaker_count = st.number_input(
            "说话人数量(可选)",
            min_value=2,
            max_value=100,
            value=config["speaker_count"] or 2,
            step=1,
        )

    # 保存配置
    if (
        api_key != config["api_key"]
        or model != config["model"]
        or vocabulary_id != config["vocabulary_id"]
        or phrase_id != config["phrase_id"]
        or ",".join(map(str, config["channel_id"])) != channel_id
        or disfluency_removal != config["disfluency_removal_enabled"]
        or timestamp_alignment != config["timestamp_alignment_enabled"]
        or special_word_filter != config["special_word_filter"]
        or diarization_enabled != config["diarization_enabled"]
        or (speaker_count != config["speaker_count"] and speaker_count != 2)
    ):
        new_config = {
            "api_key": api_key,
            "model": model,
            "vocabulary_id": vocabulary_id,
            "phrase_id": phrase_id,
            "channel_id": [int(x.strip()) for x in channel_id.split(",") if x.strip()],
            "disfluency_removal_enabled": disfluency_removal,
            "timestamp_alignment_enabled": timestamp_alignment,
            "special_word_filter": special_word_filter,
            "diarization_enabled": diarization_enabled,
            "speaker_count": speaker_count if diarization_enabled else None,
        }
        save_config(new_config)
        st.success("配置已保存")

    # 语言选择
    language = st.selectbox("选择语言", ["中文", "英语", "日语"])
    language_map = {"中文": ["zh"], "英语": ["en"], "日语": ["ja"]}

    # 输入方式选择
    input_method = st.radio("输入方式", ["上传文件", "输入URL"])

    if input_method == "上传文件":
        # 文件上传
        uploaded_file = st.file_uploader(
            "上传音频文件", type=["wav", "mp3", "m4a", "flac", "acc"]
        )

        if uploaded_file is not None:
            # 保存临时文件(二进制模式)
            original_name = uploaded_file.name
            file_ext = os.path.splitext(original_name)[1]
            with tempfile.NamedTemporaryFile(
                suffix=file_ext, mode="wb", delete=False
            ) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                file_path = tmp_file.name

            # 识别按钮
            if st.button("开始识别"):
                with st.spinner("上传文件中..."):
                    file_url = upload_file_to_dashscope(file_path)

                if file_url:
                    result = transcribe_audio(file_url, language_map[language])
                    if result:
                        st.success("识别完成")
                        file_content = ""
                        transcription_url = result.get("results")[0].get(
                            "transcription_url"
                        )
                        if transcription_url:
                            try:
                                file_content = requests.get(transcription_url).json()
                            except Exception as e:
                                st.error(f"获取结果失败: {str(e)}")

                        full_text = ""
                        full_text = file_content.get("transcripts")[0].get("text")
                        display_text = "\n\n".join(full_text)

                        st.subheader("识别结果")
                        st.text_area("文本内容", value=display_text, height=300)

                        # 保存结果
                        saved_path = save_transcription_result(
                            os.path.splitext(original_name)[0], file_content, full_text
                        )
                        if saved_path:
                            st.success(f"结果已保存到: {saved_path}")
                    else:
                        st.error("识别失败，请检查API Key和网络连接")
                else:
                    st.error("文件上传失败")

            # 删除临时文件
            if os.path.exists(file_path):
                os.unlink(file_path)
    else:
        # URL输入
        audio_url = st.text_input(
            "输入音频URL", placeholder="https://example.com/audio.wav"
        )

        if audio_url and st.button("开始识别"):
            with st.spinner("识别中..."):
                result = transcribe_audio(audio_url, language_map[language])

            if result:
                st.success("识别完成")
                # 修改部分开始
                transcription_url = result.get("results")[0].get("transcription_url")
                if transcription_url:
                    try:
                        file_content = requests.get(transcription_url).json()
                    except Exception as e:
                        st.error(f"获取结果失败: {str(e)}")
                        file_content = {}

                    full_text = file_content.get("transcripts", [{}])[0].get("text", "")
                    display_text = "\n\n".join(full_text.splitlines())  # 处理可能的换行

                    st.subheader("识别结果")
                    st.text_area("文本内容", value=display_text, height=300)

                    # 使用原始URL的文件名作为保存标识
                    original_filename = os.path.basename(audio_url).split("?")[0]
                    saved_path = save_transcription_result(
                        os.path.splitext(original_filename)[0],
                        file_content,
                        full_text,  # 保存实际转录内容而非中间结果
                    )
                    if saved_path:
                        st.success(f"结果已保存到: {saved_path}")
                else:
                    st.error("未获取到有效转录结果")


def save_transcription_result(task_id, transcription_result, full_text):
    """
    保存语音识别结果到output目录

    Args:
        task_id (str): 任务ID，用于创建子目录
        transcription_result (dict): 识别结果字典

    Returns:
        str: 保存的文件路径
    """
    try:
        config = read_config()
        # 确保output目录存在
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # 为每个任务创建独立目录
        task_dir = output_dir / task_id
        task_dir.mkdir(exist_ok=True)

        # 保存JSON文件
        output_path = task_dir / "transcription.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(transcription_result, f, ensure_ascii=False, indent=2)

        # 保存文本文件
        full_text_path = task_dir / "full_text.txt"
        with open(full_text_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        # 保存SRT字幕文件
        srt_path = task_dir / "subtitles.srt"
        subtitles = parse_transcription(
            output_path, split_speakers=config["diarization_enabled"]
        )
        main_str = subtitles["main"]
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(main_str)
        if config["diarization_enabled"]:
            for count in range(1, config["speaker_count"] + 1):
                speaker_key = f"speaker_{count}"
                if speaker_key in subtitles:
                    speaker_str = subtitles[speaker_key]
                    speaker_srt_path = task_dir / f"subtitles_{speaker_key}.srt"
                    with open(speaker_srt_path, "w", encoding="utf-8") as f:
                        f.write(speaker_str)
        return str(output_path)
    except Exception as e:
        st.error(f"保存结果失败: {str(e)}")
        return None


def parse_transcription(json_file_path, split_speakers=False):
    """解析语音识别结果JSON文件生成SRT字幕

    Args:
        json_file_path (str): JSON文件路径
        split_speakers (bool): 是否按说话人分离字幕（默认False）

    Returns:
        dict: 包含字幕内容的字典（主字幕+分角色字幕）
    """

    def ms_to_srt_time(ms):
        """将毫秒转换为SRT时间格式"""
        # 将毫秒转换为timedelta对象
        td = timedelta(milliseconds=ms)
        # 提取小时、分钟、秒和毫秒
        total_seconds = int(td.total_seconds())
        milliseconds = td.microseconds // 1000
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        # 格式化为SRT格式
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 初始化字幕字典
    subtitles = {"main": ""}
    if split_speakers:
        speaker_subtitles = {}

    # 遍历所有语音通道
    transcript = data["transcripts"][0]
    # channel_id = transcript["channel_id"]

    # 遍历所有句子
    for sentence in transcript["sentences"]:
        start_ms = sentence["begin_time"]
        end_ms = sentence["end_time"]
        text = sentence["text"].strip()

        # 处理时间格式
        start_time = ms_to_srt_time(start_ms)
        end_time = ms_to_srt_time(end_ms)

        # 主字幕内容
        subtitles["main"] += f"{start_time} --> {end_time}\n{text}\n\n"

        if split_speakers:
            speaker_id = sentence.get("speaker_id", 0)
            key = f"speaker_{speaker_id}"

            if key not in speaker_subtitles:
                speaker_subtitles[key] = ""
            speaker_subtitles[key] += f"{start_time} --> {end_time}\n{text}\n\n"

    # 合并分角色字幕
    if split_speakers:
        subtitles.update(speaker_subtitles)

    return subtitles


if __name__ == "__main__":
    main()
