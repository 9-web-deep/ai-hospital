import { createI18n } from 'vue-i18n'

const messages = {
  en: {
    common: {
      brand: 'Hospital Admin',
    },
    admin: {
      title: 'Admin Console',
      menu: {
        dashboard: 'Dashboard',
        journal: 'Journal',
      },
      dashboard: {
        title: 'Dashboard',
        welcome: 'Welcome to the admin dashboard.',
        health: {
          title: 'Service Health',
          refresh: 'Refresh',
          healthy: 'Healthy',
          unhealthy: 'Unreachable',
          unknown: 'Not Checked',
          notChecked: 'Not checked yet',
        },
        services: {
          administrator: 'Administrator',
          nurse: 'Nurse',
          customer: 'Customer',
          doctor: 'Doctor',
        },
      },
      journal: {
        title: 'Journal',
        advanced: 'Advanced Filters',
        searchPlaceholder: 'Enter keyword',
        search: 'Search',
        reset: 'Reset',
        user: 'User',
        target: 'Target',
        trace: 'Trace',
        source: 'Source',
        payload: 'Payload',
        delete: 'Delete',
        deleteConfirm: 'Delete this record?',
        deleteSuccess: 'Deleted',
        deleteFailed: 'Delete failed',
        deleteNoId: 'No id on this record',
        fetchFailed: 'Failed to load journal',
        filters: {
          traceId: 'Trace ID',
          userId: 'User ID',
          userRole: 'User Role',
          actionCode: 'Action Code',
          status: 'Status',
          targetId: 'Target ID',
          targetRole: 'Target Role',
          timeRange: 'Time Range',
        },
        empty: 'No data yet.',
      },
    },
  },
  zh: {
    common: {
      brand: '医疗管理端',
    },
    admin: {
      title: '后台管理',
      menu: {
        dashboard: '仪表盘',
        journal: '日志审计',
      },
      dashboard: {
        title: '仪表盘',
        welcome: '欢迎进入后台管理。',
        health: {
          title: '服务检测',
          refresh: '刷新',
          healthy: '正常',
          unhealthy: '不可达',
          unknown: '未检测',
          notChecked: '尚未检测',
        },
        services: {
          administrator: '管理端',
          nurse: '护士端',
          customer: '客户端',
          doctor: '医生端',
        },
      },
      journal: {
        title: '日志审计',
        advanced: '高级筛选',
        searchPlaceholder: '输入关键字',
        search: '查询',
        reset: '重置',
        user: '操作人',
        target: '目标',
        trace: '链路',
        source: '来源',
        payload: '载荷',
        delete: '删除',
        deleteConfirm: '确认删除该记录？',
        deleteSuccess: '已删除',
        deleteFailed: '删除失败',
        deleteNoId: '该记录无 id',
        fetchFailed: '加载日志失败',
        filters: {
          traceId: 'Trace ID',
          userId: '用户 ID',
          userRole: '用户角色',
          actionCode: '动作码',
          status: '状态',
          targetId: '目标 ID',
          targetRole: '目标角色',
          timeRange: '时间范围',
        },
        empty: '暂无数据。',
      },
    },
  },
} as const

const i18n = createI18n({
  legacy: false,
  locale: 'zh',
  fallbackLocale: 'en',
  messages,
})

export default i18n
