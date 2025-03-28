<template>
  <div class="main">
    <h1>这里存放主要交互界面</h1>
    <p>欢迎来到我的网站！</p>
    <div class="loginbutton" v-if="!isAuthenticated">
      <loginbutton></loginbutton>
    </div>
    <div class="ask" v-else>
      <el-input v-model="ask" placeholder="请输入你的问题" />
      <el-button type="primary" @click="handleSubmit">提交</el-button>
    </div>
  </div>
</template>

<script>
import loginbutton from '@/components/Login.vue'
import { mapGetters } from 'vuex'

export default {
  name: 'Index',
  data () {
    return {
      ask: ''
    }
  },
  components: {
    loginbutton
  },
  computed: {
    ...mapGetters('user', ['isAuthenticated'])
  },
  methods: {
    handleSubmit () {
      if (!this.isAuthenticated) {
        this.$message.warning('请先登录')
        return
      }
      // 在这里处理表单提交逻辑
      console.log(this.ask)
    }
  }
}
</script>

<style lang="less" scoped>
.main {
  width: auto;
}
.loginbutton {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
