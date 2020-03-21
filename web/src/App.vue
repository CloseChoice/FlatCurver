<template>
    <div>
        <Header />
        <div class="wrapper">
            <transition name="fade" mode="out-in">
                <router-view :key="$route.fullPath" />
            </transition>
        </div>

        <Footer />
    </div>
</template>

<script>
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'

export default {
    components: {
        Header,
        Footer,
    },

    computed: {},
}
</script>

<style scoped lang="scss">
.wrapper {
    padding-top: 0rem;
    height: 100vh;
    background: #888888;
}
</style>
