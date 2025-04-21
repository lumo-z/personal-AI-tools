<template>
  <div id="app">
    <el-container>
      <el-aside style="border-radius: 5%;">
        <el-row class="tac">
          <el-col :span="24" class="menu">
            <el-menu
              :default-active="activeIndex"
              class="el-menu-vertical-demo"
              @select="handleSelect"
              background-color="rgb(145, 115, 243)"
              text-color="#fff"
              active-text-color="#ffd04b">
              <el-menu-item index="1" @click="$router.push('/')">
                <i class="el-icon-location"></i>
                <span>首页</span>
              </el-menu-item>
              <el-menu-item index="2" @click="$router.push('/')">
                <i class="el-icon-document-add"></i>
                <span>对话</span>
              </el-menu-item>
              <el-menu-item index="3" @click="$router.push('/repository')">
                <i class="el-icon-user"></i>
                <span>个人仓库</span>
              </el-menu-item>
                <el-popover
                placement="bottom"
                width="200"
                title="请先登录"
                popper-class="el-popover"
                trigger="hover"
                :visible="false"
                @mouseover="handleMouseover"
                @mouseleave="handleMouseleave">
                  <template class="buttons" v-if="isAuthenticated">
                    <el-button @click="logout">退出登录</el-button>
                    <el-button @click="learnmore">了解更多</el-button>
                  </template>
                  <el-menu-item index="4" slot="reference">
                    <i class="el-icon-setting"></i>
                    <span >个人中心</span>
                  </el-menu-item>
                </el-popover>
            </el-menu>
          </el-col>
        </el-row>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
export default {
  name: 'App',
  data () {
    return {
      activeIndex: '1',
      popoverVisible: false
    }
  },
  methods: {
    handleSelect (index) {
      this.activeIndex = index
    },
    handleMouseover () {
      this.popoverVisible = true
    },
    handleMouseleave () {
      this.popoverVisible = false
    },
    logout () {
      // 退出登录逻辑
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$store.dispatch('user/logout')
      this.$message({
        message: '退出登录成功',
        type: 'success',
        duration: 2000,
        onClose: () => {
          window.location.reload()
        }
      })
    },
    learnmore () {
      // 了解更多逻辑
      this.$router.push('/detail')
    }
  },
  computed: {
    ...mapGetters('user', ['isAuthenticated'])
  }
}
</script>

<style lang="less" scoped>
#app {
  height: 100vh;
  display: flex;

  .el-container {
    height: 100%;

    .el-aside {
      width: 80px !important;
      background-color: rgb(145, 115, 243);
      transition: all 0.3s;

      &:hover {
        width: 180px !important;
      }
    }
  }

  .tac {
    height: 100%;
    display: flex;
    flex-direction: column;

    ::v-deep .el-menu {
      flex: 1;
      display: flex;
      flex-direction: column;

      .el-menu-item {
        height: 33%;  // 三个主要菜单项各占1/3
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-size: 14px;
        transition: all 0.3s;

        i {
          font-size: 24px;
          margin-bottom: 6px;
        }

        &:hover {
          background-color: rgba(255,255,255,0.1) !important;
        }

        &:last-child {  // 个人中心单独处理
          margin-top: auto;
          height: 60px;
        }
      }
    }
  }
}
</style>
