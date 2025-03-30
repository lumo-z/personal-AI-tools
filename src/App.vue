<template>
  <div id="app">
    <el-container>
      <el-aside style="border-radius: 5%;">
        <el-row class="tac">
        <el-col :span="24">
          <el-menu
            default-active="2"
            class="el-menu-vertical-demo"
            @open="handleOpen"
            @close="handleClose"
            background-color="rgb(145, 115, 243)"
            text-color="#fff"
            active-text-color="#ffd04b">
            <el-menu-item index="1">
              <template slot="title">
                <i class="el-icon-location"></i>
                <span>首页</span>
              </template>
            </el-menu-item>
            <el-menu-item index="2">
              <i class="el-icon-document-add"></i>
              <span slot="title">对话</span>
            </el-menu-item>
            <el-menu-item index="3">
              <i class="el-icon-user"></i>
              <span slot="title">个人仓库</span>
            </el-menu-item>
            <el-menu-item index="4">
              <i class="el-icon-setting"></i>
              <span slot="title">暂时没想好</span>
            </el-menu-item>
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
export default {
  name: 'App',
  data () {
    return {
      activeIndex: '1',
      activeIndex2: '1'
    }
  },
  methods: {
    handleOpen (key, keyPath) {
      console.log(key, keyPath)
    },
    handleClose (key, keyPath) {
      console.log(key, keyPath)
    }
  }
}
</script>
<style lang="less" scoped>
.tac {
  ::v-deep .el-menu {
    height: 100vh;
    border-right: 0;
  }
    .el-menu-item {
    height: 20%;
    line-height: 50px;
    text-align: center;
    padding-top: 30%;
    padding-bottom: 10px;
    font-size: 20px;
  }
  .el-menu-item:hover {
    background-color: #a48df3 !important;
  }
}

</style>
