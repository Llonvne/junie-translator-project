import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import FileTranslator from '@/views/FileTranslator.vue'
import TextTranslator from '@/views/TextTranslator.vue'
import Settings from '@/views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/file-translator',
    name: 'FileTranslator',
    component: FileTranslator
  },
  {
    path: '/text-translator',
    name: 'TextTranslator',
    component: TextTranslator
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router