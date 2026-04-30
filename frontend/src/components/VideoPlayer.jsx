import { useEffect, useRef } from 'react'
import Hls from 'hls.js'

export default function VideoPlayer({ urlHls }) {
  const videoRef = useRef(null)

  useEffect(() => {
    const video = videoRef.current
    if (!video || !urlHls) return

    if (Hls.isSupported()) {
      const hls = new Hls()
      hls.loadSource(urlHls)
      hls.attachMedia(video)
      return () => hls.destroy()
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = urlHls
    }
  }, [urlHls])

  return (
    <div className="bg-black aspect-video flex items-center justify-center">
      <video
        ref={videoRef}
        className="w-full h-full object-contain"
        controls
        muted
        playsInline
      />
    </div>
  )
}