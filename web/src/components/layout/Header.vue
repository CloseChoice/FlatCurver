<template>
    <b-navbar fixed-top type="is-dark">
        <template slot="brand">
            <b-navbar-item tag="router-link" :to="{ path: '/' }">
                <span class="brand">FlatCurver</span>
            </b-navbar-item>
        </template>
        <template slot="start">
            <b-navbar-item tag="router-link" :to="{ name: 'Dashboard' }">Dashboard</b-navbar-item>
            <b-navbar-dropdown label="Info">
                <b-navbar-item tag="router-link" :to="{ name: 'About' }">About</b-navbar-item>
                <b-navbar-item href="#">Privacy</b-navbar-item>
            </b-navbar-dropdown>
        </template>
    </b-navbar>
</template>

<script>
export default {}
</script>

<style lang="scss" scoped>
nav {
    padding-left: 20px;
    padding-right: 20px;
}

.brand {
    font-weight: bold;
    text-transform: uppercase;
}
</style>
