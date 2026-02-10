<template>
  <div>
    <h1>Items</h1>
    <button @click="loadItems">Load Items</button>
    <ul>
      <!-- Loop through the items and display each item's name -->
      <li v-for="item in itemStore.items" :key="item.id">{{ item.name }}</li>
    </ul>
    <form @submit.prevent="submitItem">
      <input v-model="newItem.id" placeholder="Item id" />
      <input v-model="newItem.name" placeholder="Item name" />
      <button type="submit">Add Item</button>
    </form>
    <p v-if="itemStore.error" class="error">{{ itemStore.error }}</p>
  </div>
</template>


<script lang="ts">
import { defineComponent, onMounted, ref, getCurrentInstance } from 'vue';
import { useItemStore, type Item } from '@/stores/exampleStore';

export default defineComponent({
  name: 'ExampleView',
  setup() {
    const itemStore = useItemStore();
    const newItem = ref<Item>({ id: '', name: '' });

    // Access the app instance to get $axios
    const instance = getCurrentInstance();
    const axios = instance?.appContext.config.globalProperties.$axios;

    onMounted(async () => {
      if (axios) {
        await itemStore.fetchItems(axios);
      }
    });

    const loadItems = async () => {
      if (axios) {
        await itemStore.fetchItems(axios);
      }
    };

    const submitItem = async () => {
      if (axios) {
        await itemStore.addItem(newItem.value, axios);
        newItem.value.id = '';
        newItem.value.name = '';
      }
    };

    return {
      itemStore,
      newItem,
      loadItems,
      submitItem,
    };
  },
});
</script>

<style>
.error {
  color: red;
}
</style>
