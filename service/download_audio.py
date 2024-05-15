import os
import httpx
import asyncio

from bilibili_api import video
from bilibili_api import Credential, HEADERS


async def download_url(url: str, out: str):
    async with httpx.AsyncClient(headers=HEADERS) as sess:
        resp = await sess.get(url)
        with open(out, 'wb') as f:
            process = 0
            for chunk in resp.iter_bytes(1024):
                if not chunk:
                    break
                process += len(chunk)
                f.write(chunk)

async def main():
    # 实例化 Credential 类
    credential = Credential(
        # 用于一般在获取用户对应信息时提供
        sessdata="517906ec,1730878114,2b232*52CjCI1R7G6l4QnXs_Op5Yf5X_w_fq5BOuUPPmAAbuVNqhS4djqfA8Bm7rflty8jrmUGESVnFDT0JGRWdZY0loSTJFcXlRdlVkNFdTdHczbVBvb2JRZVBtRXByVlAwNUZ4RzJhTWZORnBVMFNqdmtNYkRDTXRGa3pld280NFV2U0FGT2lLdHFhZXpnIIEC", 
        # 进行操作用户数据时提供
        bili_jct="97a07a19969a8718b495822d18f2a653", 
        # 设备验证码，放映室内部分接口需要提供
        buvid3="CBD25AD3-9D69-C083-A8C2-6DD0EE0DE77676843infoc", 
        # 用户 UID，通常不需要提供
        dedeuserid="3546632433960971",    
        # 在登录时获取，登录状态过期后用于刷新 Cookie 
        ac_time_value="ba6fc7f0d7a34157a90ad293fb4f8b52"  
    )
    # 实例化 Video 类
    v = video.Video(bvid="BV1dE42157MK", credential=credential)
    # 获取视频下载链接
    download_url_data = await v.get_download_url(0)
    # 解析视频下载信息
    detecter = video.VideoDownloadURLDataDetecter(data=download_url_data)
    streams = detecter.detect_best_streams()
    idx, filename = (
        (0, "flv_temp.flv")
        if detecter.check_flv_stream() == True else
        (1, "audio_temp.m4s")
    )
    await download_url(streams[idx].url, filename)



if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
