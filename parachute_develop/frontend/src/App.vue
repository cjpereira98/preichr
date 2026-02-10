<template>
  <div id="app">
    <!-- Layout -->
    <div class="layout">
      <!-- Drawer -->
      <div :class="['drawer', { 'drawer-open': isDrawerOpen }]">
        <div class="menu-items">
          <a class="menu-header">
            <img alt="SWF2 logo" class="logo menu-icon" src="@/assets/logo.png" />
            <span class="menu-header-text" v-if="!isDrawerOpen">SWF2 Parachute</span>
          </a>
          <RouterLink
            v-for="link in links"
            :key="link.name"
            :to="link.path"
            class="menu-item"
            :class="{ 'menu-item-active': isActive(link.path) }"
          >
            <VIcon :name="link.icon" class="menu-icon" />
            <span class="menu-text" v-if="!isDrawerOpen">{{ link.name }}</span>
          </RouterLink>
        </div>
      </div>

      <!-- Main Content -->
      <div :class="['main-content', { 'drawer-open': isDrawerOpen }]">
        <button class="menu-toggle" @click="toggleDrawer">
          <VIcon name="co-hamburger-menu" class="toggle-icon" />
        </button>
        <RouterView />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRoute } from 'vue-router';
import { OhVueIcon, addIcons } from 'oh-vue-icons';
import { CoHamburgerMenu, CoHome, BiBalloonHeart, CoServerFault, BiPersonLinesFill, CoCog } from 'oh-vue-icons/icons';

addIcons(CoHamburgerMenu, CoHome, BiBalloonHeart, CoServerFault, BiPersonLinesFill, CoCog);

export default defineComponent({
  name: 'App',
  components: {
    VIcon: OhVueIcon,
  },
  setup() {
    const isDrawerOpen = ref(false); // Drawer open by default
    const route = useRoute();

    const toggleDrawer = () => {
      isDrawerOpen.value = !isDrawerOpen.value;
    };

    const links = [
      { name: 'Home', path: '/', icon: 'co-home' },
      { name: 'Example', path: '/example', icon: 'bi-balloon-heart' },
      { name: 'PS Staffing Plan', path: '/staffing_plan', icon: 'co-server-fault' },
      { name: 'AM Scorecard', path: '/am_scorecard', icon: 'bi-person-lines-fill' },
      { name: 'Settings', path: '/settings', icon: 'co-cog' },
    ];

    const isActive = (path: string) => route.path === path;

    return {
      isDrawerOpen,
      toggleDrawer,
      links,
      isActive,
    };
  },
});
</script>

<style scoped>
/* General Layout */
#app {
  font-family: 'Arial', sans-serif;
  color: #333;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.menu-toggle {
  background: none;
  border: none;
  color: white;
  font-size: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  margin-right: 10px;
  margin: -5px 0px 45px -10px;
}

.toggle-icon {
  color: #333;
  border: 1px solid #333;
  padding: 2px;
  border-radius: 5px;
  width: 20px;
  height: 20px;
}

/* Layout */
.layout {
  display: flex;
  height: calc(100vh - 60px); /* Subtract header height */
}


/* Drawer */
.drawer {
  width: 200px;
  background-color: #20232a;
  color: white;
  height: 100%;
  transition: width 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.drawer-open {
  width: 65px;
}

/* Menu Items */
.menu-items {
  margin-top: 5px;
  display: flex;
  flex-direction: column;
}

.menu-header,
.menu-item {
  text-decoration: none;
  color: #b0b3c7;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  transition: background-color 0.3s ease, color 0.3s ease;
  font-size: 16px;
}

.menu-header {
  padding: 15px 10px;
}

.menu-header-text {
  border-left: 1px solid #e1e1e1;
  padding-left: 10px;
  font-size: 18px;
  line-height: 18px;
  color: #e1e1e1;
}

.logo {
  display: inline;
  margin-right: 5px;
  width: 40px;
  height: 40px;
}

.menu-item:hover {
  background-color: #3a3b4f;
  color: white;
}

.menu-item-active {
  background-color: #484a5e;
  color: white;
}

.menu-icon {
  font-size: 20px;
  margin-right: 10px;
  color: #FFF;
}

.menu-text {
  font-size: 16px;
  line-height: 18px;
  color: #e1e1e1;
}

/* Main Content */
.main-content {
  flex: 1;
  border-radius: 5px;
  background-color: #f4f4f8;
  color: #333;
  padding: 20px;
  overflow-y: auto;
  transition: margin-left 0.3s ease-in-out;
}

.drawer-open + .main-content {
  margin-left: 0px;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .drawer {
    width: 65px;
  }

  .drawer-open {
    width: 65px;
  }

  .menu-text {
    display: none;
    line-height: 18px;
  }

  .main-content {
    margin-left: 70px;
  }
}
</style>
