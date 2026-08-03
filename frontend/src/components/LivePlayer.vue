<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import videojs from 'video.js'

const props = defineProps<{ src: string }>()

const playerElement = ref<HTMLVideoElement | null>(null)
let player: ReturnType<typeof videojs> | null = null

onMounted(async () => {
  await nextTick()
  if (playerElement.value) {
    player = videojs(playerElement.value, {
      controls: true,
      autoplay: false,
      fluid: true,
      sources: [{ src: props.src, type: 'application/x-mpegURL' }],
    })
  }
})

onBeforeUnmount(() => {
  if (player) {
    player.dispose()
    player = null
  }
})
</script>

<template>
  <video ref="playerElement" class="video-js vjs-big-play-centered" />
</template>
