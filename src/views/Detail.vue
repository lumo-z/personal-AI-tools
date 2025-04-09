<template>
  <div>
    <el-button type="primary" @click="handleClick">
      详情
    </el-button>
    <el-dialog title="详情" :visible.sync="dialogVisible">
      <p>这是一个详情对话框</p>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'Detail'
}
</script>

<style lang="less" scoped></style>
