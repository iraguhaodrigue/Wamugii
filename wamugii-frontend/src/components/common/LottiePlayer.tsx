import { useRef } from 'react'
import { LottieInteractions, LottieSvg, lottieInView, type LottieHandle } from 'lottie-react'

export interface LottiePlayerProps {
  src: string
  loop: boolean
  reduceMotion: boolean
  onError: () => void
}

/**
 * The lazy half of LottieOnView, kept in its own module so the engine gets its
 * own chunk — `lottie-react` pulls in lottie-web, which is larger than
 * anything else the public site loads, and none of it belongs in the entry
 * bundle.
 *
 * `src` is a URL that the library fetches itself, so deferring this module
 * defers the animation JSON along with the engine.
 *
 * `LottieSvg` rather than `Lottie`: it carries only the svg renderer instead
 * of all three, and still keeps the expression engine, so animations whose
 * properties are expression-driven play as designed.
 */
export default function LottiePlayer({ src, loop, reduceMotion, onError }: LottiePlayerProps) {
  const handle = useRef<LottieHandle>(null)

  // Reduced motion: load and show the finished picture, never animate. Seeking
  // on `ready` to 100% rather than computing a frame number keeps this right
  // for any animation's length.
  if (reduceMotion) {
    return (
      <LottieSvg
        src={src}
        loop={false}
        autoplay={false}
        lottieRef={handle}
        className="size-full"
        subscriptions={{
          ready: () => handle.current?.seek({ percent: 100 }),
          error: () => onError(),
        }}
      />
    )
  }

  // `lottieInView` plays on entry and pauses on exit, resuming mid-motion
  // rather than restarting. It also covers the case where the element is
  // entered while the JSON is still in flight — it plays once the load lands —
  // which is why playback is left to it instead of being driven from the
  // wrapper's own observer.
  //
  // `once` for a non-looping animation, so scrolling away and back does not
  // replay a one-shot.
  return (
    <LottieInteractions interactions={[lottieInView({ once: !loop })]}>
      <LottieSvg
        src={src}
        loop={loop}
        autoplay={false}
        className="size-full"
        subscriptions={{ error: () => onError() }}
      />
    </LottieInteractions>
  )
}
