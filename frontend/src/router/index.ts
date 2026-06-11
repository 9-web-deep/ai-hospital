import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import AdminDashboard from '@/views/admin/Dashboard.vue'
import AdminJournal from '@/views/admin/Journal.vue'
import NurseChat from '@/views/nurse/Chat.vue'
import NotFound from '@/views/NotFound.vue'
import CtAnalyze from '@/views/doctor/CtAnalyze.vue'
import DoctorDispensing from '@/views/doctor/Dispensing.vue'
import DoctorInfusion from '@/views/doctor/Infusion.vue'
import NurseDispensingRequest from '@/views/nurse/DispensingRequest.vue'
import NurseDispensingTasks from '@/views/nurse/DispensingTasks.vue'
import NurseInfusionTasks from '@/views/nurse/InfusionTasks.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/admin/dashboard',
  },
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { title: 'Dashboard' },
      },
      {
        path: 'journal',
        name: 'AdminJournal',
        component: AdminJournal,
        meta: { title: 'Journal' },
      },
    ],
  },
  {
    path: '/nurse/chat',
    name: 'NurseChat',
    component: NurseChat,
  },
  {
    path: '/doctor/ct',
    name: 'DoctorCtAnalyze',
    component: CtAnalyze,
  },
  {
    path: '/doctor/dispensing',
    name: 'DoctorDispensing',
    component: DoctorDispensing,
  },
  {
    path: '/doctor/infusion',
    name: 'DoctorInfusion',
    component: DoctorInfusion,
  },
  {
    path: '/nurse/dispensing/request',
    name: 'NurseDispensingRequest',
    component: NurseDispensingRequest,
  },
  {
    path: '/nurse/dispensing/tasks',
    name: 'NurseDispensingTasks',
    component: NurseDispensingTasks,
  },
  {
    path: '/nurse/infusion/tasks',
    name: 'NurseInfusionTasks',
    component: NurseInfusionTasks,
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
