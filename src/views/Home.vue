<template>
  <el-container>
    <el-aside width="200px">
      <h1>历史纪录</h1>
      <ul>
        <li v-for="item in history" :key="item.id">
          <el-button type="text" @click="handleHistoryClick(item)">
            {{ item.question }}
          </el-button>
        </li>
      </ul>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script>
// import { mapGetters } from 'vuex'
import { GetHistoryApi } from '@/api/history'
export default {
  data () {
    return {
      history: [], // 用于存储历史记录的数组
      currentQuestion: '' // 当前问题的输入
    }
  },
  methods: {
    async getHistory () {
      const history = await GetHistoryApi().then(res => {
        return res.data.data
      }).catch(err => {
        console.error(err)
        this.$message.error('获取历史记录失败')
        return []
      })
      return history
    },
    handleHistoryClick (item) {
      // 处理历史记录点击事件，将问题内容赋值给 currentQuestion
      this.currentQuestion = item.question
    }
  },
  created () {
    // 从本地存储中获取历史记录
    this.history = this.getHistory()
  }
}
</script>

<style lang="less" scoped>
//::v-deep 样式穿透
</style>
