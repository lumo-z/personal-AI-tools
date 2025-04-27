<template>
  <el-container class="main">
      <el-aside width="200px" style="height: auto;">
        <h1>历史纪录：</h1>
        <ul v-if="history.length > 0">
          <li v-for="item in history" :key="item.id">
            <el-button type="text" @click="handleHistoryClick(item)">
              {{ item.title }}
            </el-button>
          </li>
        </ul>
        <div v-else>
          暂无历史记录
        </div>
      </el-aside>
    <el-container>
      <el-main class="chat-area">
        <div class="message-list" ref="messageList">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message-item', message.sender]"
          >
            <div class="message-avatar">
              <el-avatar :src="message.sender === 'user' ? userAvatar : aiAvatar"></el-avatar>
            </div>
            <div class="message-content">
              <div v-if="message.think" class="think-content">
                <i class="el-icon-info"></i> 思考过程: {{ message.think }}
              </div>
              <div class="message-text" v-html="marked(message.text)"></div>
              <div class="message-time">{{ formatTime(message.time) }}</div>
            </div>
          </div>
          <div v-if="isLoading" class="message-item ai">
            <div class="message-avatar">
              <el-avatar :src="aiAvatar"></el-avatar>
            </div>
            <div class="message-content">
              <div class="message-text">
                <i class="el-icon-loading"></i> AI正在思考中...
              </div>
            </div>
          </div>
        </div>
      </el-main>

      <el-footer class="input-area" style="height: auto;">
        <div class="loginbutton" v-if="!isAuthenticated">
          <loginbutton></loginbutton>
        </div>
        <div class="input-container" v-else>
          <el-input
            v-model="ask"
            placeholder="请输入你的问题"
            type="textarea"
            :rows="2"
            :autosize="{ minRows: 2, maxRows: 6 }"
            @keyup.enter.native.prevent="handleInput"
            @keydown.enter.shift.native="handleKeydown"
            resize="none"
          ></el-input>
          <el-button
            type="primary"
            @click="handleSubmit"
            :loading="isLoading"
            class="submit-btn"
          >
            发送
          </el-button>
        </div>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script>
import loginbutton from '@/components/Login.vue'
import { GetDetailHistoryApi, GetHistoryApi } from '@/api/history'
import { mapGetters } from 'vuex'
import { marked } from 'marked'
import _ from 'lodash'
export default {
  name: 'Index',
  data () {
    return {
      ask: '',
      history: [],
      messages: [],
      isLoading: false,
      userAvatar: require('@/assets/user.jpg'),
      aiAvatar: require('@/assets/ai.jpg')
    }
  },
  components: {
    loginbutton
  },
  computed: {
    ...mapGetters('user', ['isAuthenticated'])
  },
  methods: {
    async handleSubmit () {
      if (!this.isAuthenticated) return this.$message.warning('请先登录')
      if (!this.ask.trim()) return
      const question = this.ask.trim()
      // 添加消息
      this.messages.push(
        { sender: 'user', text: this.ask, time: new Date() },
        { sender: 'ai', text: '', think: '', time: new Date() }
      )
      const aiMsg = this.messages[this.messages.length - 1]

      this.isLoading = true
      let eventSource = null
      try {
        const BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000'
        const url = new URL(`${BASE_URL}/api/ask/sse`)
        url.searchParams.append('question', encodeURIComponent(question))
        url.searchParams.append('t', Date.now()) // 防止缓存
        eventSource = new EventSource(url.toString(), {
          withCredentials: true
        })

        const handlers = {
          status: e => {
            if (JSON.parse(e.data).status === 'end') {
              eventSource.close()
              // const data = {
              //   user_id: this.$store.state.user.user.id,
              //   session_id: this.generateSessionId(),
              //   question: question,
              //   answer: '<think>' + aiMsg.think + '<think>' + '<answer>' + aiMsg.text + '<answer>',
              //   timestamp: new Date().getTime()
              // }
              // SaveHistoryApi(data).then(res => {
              //   console.log(res.data.message)
              // }).catch(err => {
              //   console.log(err)
              //   this.$message.error('保存历史记录失败')
              // })
              this.isLoading = false
            }
          },
          think: e => {
            this.$set(aiMsg, 'think', JSON.parse(e.data).content)
            this.scrollToBottom()
          },
          message: e => {
            console.log(e.data)
            this.$set(aiMsg, 'text', aiMsg.text + JSON.parse(e.data).content)
            this.scrollToBottom()
          },
          error: e => {
            this.$message.error(JSON.parse(e.data).error || '请求出错')
            eventSource.close()
            this.isLoading = false
          }
        }

        Object.entries(handlers).forEach(([type, handler]) => {
          eventSource.addEventListener(type, handler)
        })

        // 添加连接关闭时的清理
        eventSource.onerror = () => {
          if (eventSource.readyState === EventSource.CLOSED) {
            this.isLoading = false
          }
        }
      } catch (err) {
        console.error(err)
        this.$message.error('请求出错')
        if (eventSource) eventSource.close()
      } finally {
        this.ask = ''
        this.isLoading = false
      }
    },
    formatTime (time) {
      const date = new Date(time)
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    },
    scrollToBottom: _.debounce(function () {
      this.$nextTick(() => {
        this.$refs.chatContainer?.scrollTo({
          top: this.$refs.chatContainer.scrollHeight,
          behavior: 'smooth'
        })
      })
    }, 100),
    handleInput (event) {
      if (!event.shiftKey) {
        this.handleSubmit()
      }
    },
    handleKeydown () {
      this.ask += '\n'
    },
    async getHistory () {
      const userId = this.$store.state.user.user.id
      const history = await GetHistoryApi(userId).then(res => {
        return res.data.data
      }).catch(err => {
        console.error(err)
        this.$message.error('获取历史记录失败')
        return []
      })
      return history
    },
    async handleHistoryClick (item) {
      // 处理历史记录点击事件，将问题内容赋值给 currentQuestion
      const data = GetDetailHistoryApi({
        userId: item.id,
        sessionId: item.session
      }).then(res => {
        return res.data.data
      }).catch(err => {
        console.error(err)
        this.$message.error('获取历史记录失败')
        return []
      })
      this.messages = data.records.flatMap(item => {
        return [
          {
            sender: 'user',
            text: item.question,
            time: new Date(item.timestamp)
          },
          {
            sender: 'ai',
            text: item.answer,
            time: new Date(item.timestamp)
          }
        ]
      })
    },
    generateSessionId () {
    // 获取当前时间的时间戳（毫秒级）
      const timestamp = new Date().getTime()

      // 生成一个随机数（0到1之间的浮点数，然后放大并取整）
      const randomNum = Math.floor(Math.random() * 1000000)

      // 将时间戳和随机数组合在一起
      const sessionId = `${timestamp}-${randomNum}`

      return sessionId
    },
    marked (text) {
      return marked(text)
    }
  }
}
</script>

<style lang="less" scoped>
.main {
  height: 100vh;
  .el-aside {
    border-right: 1px solid #e6e6e6;
    padding: 20px;
  }
    .el-container {
      overflow: hidden;
      display: flex;
      flex-direction: column;
      .chat-area {
      padding: 20px,0px;
      flex: 1;
      overflow: hidden;
      display: flex;
    }
     .el-footer {
      display: flex;
      flex-direction: column;
      padding: 10px;
      .input-area {
      display: flex;
      background: #fff;
      border-top: 1px solid #eee;
      .input-container {
        width: 100%;
        .el-input {
        margin-top: 10px;
        width: 100%;
        height: auto;
       }
      }
      .submit-btn {
        margin-top: 10px;
        margin-left: 200px;
       }
    }
     }
  }
}
/* 修改消息区域样式 */
.message-list {
  height: 80%;
  overflow-y: auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  &.user {
    justify-content: flex-end;
  }
  &.ai {
    justify-content: flex-start;
  }
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  .message-item.user & {
    background-color: #e3f2fd;
  }
  .message-item.ai & {
    background-color: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
}

/* 新增思考内容样式 */
.think-content {
  font-size: 14px;
  color: #999;  /* 淡灰色字体 */
  font-style: italic;
  margin-bottom: 8px;
  padding: 8px;
  background-color: #f5f5f5;
  border-left: 3px solid #ddd;
  border-radius: 4px;
}

.message-text {
  line-height: 1.6;
  word-break: break-word;
  /* 保留原有markdown样式 */
  & /deep/ p {
    margin: 0 0 10px;
  }
  & /deep/ code {
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: monospace;
  }
  & /deep/ pre {
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 3px;
    overflow-x: auto;
  }
  & /deep/ blockquote {
    border-left: 4px solid #ddd;
    padding-left: 15px;
    color: #777;
  }
}
</style>
