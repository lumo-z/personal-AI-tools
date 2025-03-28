<template>
  <el-container>
    <el-aside width="200px">
      <h1>用于存放问答的历史纪录</h1>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script>
export default {
  data () {
    return {
    }
  },
  methods: {
  }
}
</script>

<style lang="less" scoped>
//::v-deep 样式穿透
</style>
