// 通用格式化函数
export const formatDate = (date) => {
  if (!date) return '未定'
  try {
    return new Date(date).toLocaleString('zh-CN')
  } catch {
    return date
  }
}
