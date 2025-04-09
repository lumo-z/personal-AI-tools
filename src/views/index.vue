<template>
  <div class="main">
    <h1>这里存放主要交互界面</h1>
    <div class="loginbutton" v-if="!isAuthenticated">
      <loginbutton></loginbutton>
    </div>
    <div class="ask" v-else>
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
              <div class="message-text" v-html="message.text"></div>
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

      <el-footer class="input-area">
        <div class="input-container">
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
        <div class="tips">
          <span>提示:按Enter发送,Shift+Enter换行</span>
        </div>
      </el-footer>
    </div>
  </div>
</template>

<script>
import loginbutton from '@/components/Login.vue'
// import { askApi } from '@/api/ask'
import { mapGetters } from 'vuex'
export default {
  name: 'Index',
  data () {
    return {
      ask: '',
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

        // 修改handleSubmit中的URL
        eventSource = new EventSource(`${BASE_URL}/api/ask/sse?question=${encodeURIComponent(this.ask)}&t=${Date.now()}`)

        const handlers = {
          status: e => {
            if (JSON.parse(e.data).status === 'end') {
              eventSource.close()
              this.isLoading = false
            }
          },
          think: e => {
            this.$set(aiMsg, 'think', JSON.parse(e.data).content)
            this.scrollToBottom()
          },
          message: e => {
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
        this.$message.error('请求失败')
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
    scrollToBottom () {
      this.$nextTick(() => {
        const container = this.$refs.messageList
        container.scrollTop = container.scrollHeight
      })
    },
    handleInput (event) {
      if (!event.shiftKey) {
        this.handleSubmit()
      }
    },
    handleKeydown () {
      this.ask += '\n'
    }
  }
}
</script>

<style lang="less" scoped>
.main {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-item {
  display: flex;
  gap: 15px;

  &.user {
    flex-direction: row-reverse;
  }
}

.message-content {
  max-width: 70%;
  .think-content {
    color: #999;
    font-size: 14px;
    margin-bottom: 5px;
  }
}

.message-text {
  padding: 10px 15px;
  border-radius: 8px;

  .user & {
    background: #409EFF;
    color: white;
  }

  .ai & {
    background: #f5f5f5;
  }
}

.input-area {
  padding: 15px;
  border-top: 1px solid #eee;
}

.input-container {
  display: flex;
  gap: 10px;
}

.submit-btn {
  align-self: flex-end;
}
</style>
