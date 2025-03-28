# 视频（mp4格式）和脚本位于同一路径下，并在该路径下运行脚本（双击或命令行）

import os
import time
import subprocess
import json

# 检测视频编码类型的函数
def get_video_codec(file_path):
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of json "{file_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        codec = data['streams'][0]['codec_name'].lower()
        return codec
    except:
        # 如果解析失败，默认返回h264
        return "h264"

# 重命名后视频序列形为："v (1).mp4"、"v (2).mp4"、"v (3).mp4"……
n = input('按合并次序倒序选中视频并重命名为v，然后输入视频总数：')
n = int(n)

# mp4转ts - 自动检测并使用正确的比特流过滤器
for i in range(n):
    i = i+1
    input_file = f'"v ({i}).MOV"'
    
    # 检测视频编码类型
    codec = get_video_codec(input_file.strip('"'))
    
    # 根据编码选择适当的过滤器
    if codec == "hevc":
        bsf = "hevc_mp4toannexb"
    else:  # 默认使用h264
        bsf = "h264_mp4toannexb"
    
    print(f"处理文件 {input_file}，检测到编码: {codec}，使用过滤器: {bsf}")
    
    # 构建命令并执行
    cm = f'ffmpeg -i {input_file} -c copy -f mpegts -bsf:v {bsf} {i}.ts'
    os.system(cm)

# 合并ts
# copy /b 1.ts+2.ts+3.ts tempfile.tmp
series = ''
for i in range(n):
    i = i+1
    series += str(i) + '.ts'
    if i < n:
        series += '+'
cm = 'copy /b ' + series +' tempfile.tmp'
os.system(cm)

# ts转mp4
# ffmpeg -i tempfile.tmp -c copy -bsf:a aac_adtstoasc
# 防止输出重名，添加unix时间后缀
current_time = int(time.time())
outPutName = f'merge{current_time}.mp4'
cm = 'ffmpeg -i tempfile.tmp -c copy -bsf:a aac_adtstoasc ' + outPutName
os.system(cm)

# 删除临时文件
for i in range(n):
    i = str(i+1) + '.ts'
    os.remove(i)
os.remove('tempfile.tmp')

input('任务结束，按回车键退出')
