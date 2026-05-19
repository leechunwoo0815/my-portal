<template>
  <div>
    <a
      :href="`#${item.id}`"
      :class="['toc-link', `toc-level-${item.level}`, { active: activeId === item.id }]"
      @click.prevent="scrollTo(item.id)"
    >
      {{ item.text }}
    </a>
    <div v-if="item.children && item.children.length" class="toc-children">
      <TocNode
        v-for="child in item.children"
        :key="child.id"
        :item="child"
        :active-id="activeId"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TocItem } from '@/composables/useToc'

defineProps<{
  item: TocItem
  activeId: string
}>()

const scrollTo = (id: string) => {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>

<style scoped>
.toc-link {
  display: block;
  padding: 4px 8px;
  font-size: 13px;
  color: var(--app-text-secondary);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
  line-height: 1.4;
  border-left: 2px solid transparent;
}
.toc-link:hover {
  color: var(--app-text);
  background: var(--app-bg);
}
.toc-link.active {
  color: var(--cyber-neon, #00d4aa);
  border-left-color: var(--cyber-neon, #00d4aa);
  background: rgba(0, 212, 170, 0.05);
}
.toc-level-1 { padding-left: 8px; font-weight: 600; }
.toc-level-2 { padding-left: 20px; }
.toc-level-3 { padding-left: 32px; font-size: 12px; }
.toc-level-4 { padding-left: 44px; font-size: 12px; }
.toc-children { display: flex; flex-direction: column; }
</style>
