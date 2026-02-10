// src/stores/itemStore.ts
import { defineStore } from 'pinia';
import type { AxiosInstance, AxiosError } from 'axios';

// Define the Item interface
export interface Item {
  id: string;
  name: string;
}

// Define the State interface
export interface State {
  items: Item[];
  error: string | null;
}

// Define the Pinia store
export const useItemStore = defineStore('example', {
  state: (): State => ({
    items: [],
    error: null,
  }),
  actions: {
    async fetchItems(axios: AxiosInstance): Promise<void> {
      this.error = '';
      try {
        const response = await axios.get<Item[]>('/example/all');
        // Directly assign the array of items to the state
        this.items = response.data;
      } catch (error: unknown) {
        const axiosError = error as AxiosError;
        this.error =
          (axiosError.response?.data as string) ||
          axiosError.message ||
          'Failed to fetch items';
      }
    },

    async addItem(newItem: Item, axios: AxiosInstance): Promise<void> {
      this.error = '';
      try {
        const response = await axios.post<Item>('/example/add', newItem);
        this.items.push(response.data); // Update the store with the new item
      } catch (error: unknown) {
        const axiosError = error as AxiosError;
        this.error =
          (axiosError.response?.data as string) ||
          axiosError.message ||
          'Failed to add item';
      }
    },
  },
});
