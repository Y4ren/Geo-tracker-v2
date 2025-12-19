<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { fetchUserById, fetchUserDuels } from "../api";
import { TrendingUpDown } from "lucide-vue-next";
import DuelHistory from "../components/DuelHistory.vue";
import RankingGraph from "../components/RankingGraph.vue"

const route = useRoute();
let userId = route.params.id;

const user = ref<any>(null);
var duelsData = ref<any[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

var offset = 0;
var limit = 10;

onMounted(async () => {
  await loadUserInfo();
});

watch(() => route.fullPath, () => {
  userId = route.params.id;
  loadUserInfo();
})

async function loadUserInfo(){
  if (!userId) return;
  
  loading.value = true;
  try {
    user.value = await fetchUserById(userId);
    duelsData.value = await fetchUserDuels(userId, limit, offset);
  } catch (err: any) {
    error.value = err.message || "Failed to fetch user";
  } finally {
    loading.value = false;
  }
}

function openProfile() {
  if (!user.value || !user.value.username) return;
  const profileUrl = `https://www.geoguessr.com/user/${user.value.id}`;
  window.open(profileUrl, "_blank");
}
</script>

<template>
  <div class="flex flex-col items-center gap-3 py-8 px-4">
   <div class="glass flex w-full max-w-5xl min-w-[800px] gap-6">
      <div class="flex items-center gap-4 p-4">
        <div class="relative w-25 h-25 rounded-full overflow-hidden bg-gray-200 border-3 border-white">
            <img
            v-if="user?.avatar_url"
            :src="`https://www.geoguessr.com/images/resize:auto:300:300/gravity:ce/plain/${user?.avatar_url}`"
            class="rounded-full object-cover absolute top-0 left-1/2 -translate-x-1/2 w-auto h-[170%]"
            />
        </div>
        <div class="flex flex-col">
          <div class="text-2xl font-bold flex items-center">
            <div
            :class="`fi fi-${user?.country_code.toLowerCase()}`"
            class="w-4 h-4"
            ></div>
            {{ user?.username }}
          </div>
          <div class="w-6 h-6 hover:cursor-pointer glass rounded p-0.5" @click="openProfile">
            <img src="../assets/geoguessr.png" alt="">
          </div>
        </div>
      </div>
   </div>
    <div class="flex w-full max-w-5xl min-w-[800px] gap-6">
      <div class="flex flex-col flex-1 gap-4">
        <div class="glass p-4">
          <ranking-graph :user-id="userId" />
        </div>
        <div class="glass p-4 glow-green">
          <h3 class="text-gray-400 flex justify-between">
            <div>
              Best countries
            </div>
            <div>
              Delta
            </div>
          </h3>
          <div class="flex justify-between">
            <h2><span class="fi fi-fr rounded-sm"></span> France</h2>
            <h2 class="text-green-300">+732</h2>
          </div>
          <div class="flex justify-between">
            <h2><span class="fi fi-jp rounded-sm"></span> Japan</h2>
            <h2 class="text-green-300">+364</h2>
          </div>
          <div class="flex justify-between">
            <h2><span class="fi fi-us rounded-sm"></span> United-States</h2>
            <h2 class="text-green-300">+257</h2>
          </div>
        </div>
          <div class="glass p-4 glow-red">
          <h3 class="text-gray-400 flex justify-between">
            <div>
              Worst countries
            </div>
            <div>
              Delta
            </div>
          </h3>
          <div class="flex justify-between">
            <h2><span class="fi fi-no rounded-sm"></span> Norway</h2>
            <h2 class="text-red-300">-946</h2>
          </div>
          <div class="flex justify-between">
            <h2><span class="fi fi-br rounded-sm"></span> Brazil</h2>
            <h2 class="text-red-300">-578</h2>
          </div>
          <div class="flex justify-between">
            <h2><span class="fi fi-ru rounded-sm"></span> Russia</h2>
            <h2 class="text-red-300">-351</h2>
          </div>
        </div>
      </div>

      <div class="flex flex-col flex-3 gap-6">
        <div class="glass">
          <h3 class="text-gray-400 flex items-center justify-center gap-2 p-3">
            <TrendingUpDown class="w-4 h-4"/>
            Game history
          </h3>
        </div>
        <div class="flex flex-col gap-1">
          <DuelHistory
            v-for="duel in duelsData"
            :key="duel.id+userId"
            :duel="duel"
          />
        </div>
      </div>

    </div>
  </div>
</template>
