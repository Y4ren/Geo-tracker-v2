<script setup>
import { fetchUsers } from '../api';
import { ref } from 'vue';
import { useRouter } from 'vue-router'

const router = useRouter();
let users = ref([]);

function searchUser(element) {
    if(element.target.value.length < 1) 
    return;
    fetchUsers(element.target.value, 10, 0).then((data) => {
        users.value = data;
    });
}

function goToProfile(user) {
  router.push(`/users/${user.id}`)
}
</script>

<template>
    <div class="relative flex justify-center items-start pt-20 w-full">
        <div class="relative w-96">
            <input
            class="glass w-full p-4 h-14 rounded-full focus:outline-none focus:ring-1 focus:ring-fuchsia-400 transition-all"
            placeholder="Search a user..."
            @input="searchUser"
            />
            
            <transition name="fade">
                <div
                v-if="users.length"
                class="absolute top-16 w-full glass bg-black/30 border border-white/10 rounded-2xl overflow-hidden shadow-lg backdrop-blur-xl z-10"
                >
                <div
                v-for="user in users"
                :key="user.id"
                class="flex items-center gap-3 px-4 py-3 hover:bg-white/10 transition cursor-pointer"
                @click="goToProfile(user)"
                >
                <div class="relative w-10 h-10 rounded-full overflow-hidden border-0 border-white">
                    <img
                    v-if="user.avatar_url"
                    :src="`https://www.geoguessr.com/images/resize:auto:100:100/gravity:ce/plain/${user.avatar_url}`"
                    class="rounded-full object-cover absolute top-0 left-1/2 -translate-x-1/2 w-auto h-[170%]"
                    />
                </div>
                <div class="flex flex-col">
                    <div class="text-gray-100 font-semibold">
                        {{ user.username }} 
                        <div
                        :class="`fi fi-${user.country_code.toLowerCase()}`"
                        class="w-3 h-3 rounded-fm"
                        ></div>
                    </div>
                    <span class="text-xs text-gray-400">Rating: {{ user.rating }}</span>
                </div>
            </div>
        </div>
    </transition>
</div>
</div>
</template>