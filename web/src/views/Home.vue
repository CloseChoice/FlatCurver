<template>
    <div class="home">
        <div class="container is-fluid">
            <div id="kf-embed-container-2c3a19f34cbe761c8b25c92e1ef93936" class="klip"></div>
        </div>
    </div>
</template>

<script>
import klipfolio from '@/plugins/klipfolio.js'
export default {
    name: 'Home',
    components: {},

    mounted() {
        klipfolio()

        window.KF.embed.embedKlip({
            profile: '2c3a19f34cbe761c8b25c92e1ef93936',
            settings: { width: 500, theme: 'dark', borderStyle: 'square', borderColor: '#cccccc' },
            title: 'Corona Statistics',
        })
    },
}
</script>

<style scoped lang="scss">
.home {
    padding-top: 20px;
}

.klip {
    display: block !important;
    width: 50%;
    min-width: 350px;
    margin: 0 auto;
}
</style>
