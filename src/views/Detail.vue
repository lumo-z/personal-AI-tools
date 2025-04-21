<template>
  <div>
    <el-form v-model="form">
      <el-form-item label="姓名" prop="name">
        <el-input v-model="form.name"></el-input>
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email"></el-input>
      </el-form-item>
      <el-form-item label="电话" prop="phone">
        <el-input v-model="form.phone"></el-input>
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="save">保存</el-button>
        <el-button @click="cancel">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'Detail',
  data () {
    return {
      form: {
        name: '',
        email: '',
        phone: '',
        remark: ''
      }
    }
  },
  created () {
    // 获取详情数据
    this.getDetail()
  },
  methods: {
    getDetail () {
    }
  }
}
</script>

<style lang="less" scoped></style>
