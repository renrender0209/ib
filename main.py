from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os

app = FastAPI()

# どこからでも（Workerからでも）アクセスできるように許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get")
def get_video_url(v: str = Query(..., description="YouTubeの動画ID")):
    video_url = f"https://www.youtube.com/watch?v={v}"
    
    # 【重要】Cookie更新を不要にするための最新の設定
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                # 複数のクライアントを試すことで、ボット判定を回避しやすくする
                'player_client': ['android_testsuite', 'web_embedded', 'ios'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        # プロキシなしでも成功率を上げるためのヘッダー偽装
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 14; ja_JP) gzip',
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # 再生に必要な直リンクを抽出
            return {
                "success": True,
                "title": info.get('title'),
                "url": info.get('url'), # これが googlevideo.com の直リンク
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration')
            }
    except Exception as e:
        # エラーが出た場合はその内容を返す（デバッグ用）
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
