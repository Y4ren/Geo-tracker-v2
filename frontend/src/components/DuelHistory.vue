<script setup lang="ts">
import { ref, nextTick, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
    CollapsibleRoot,
    CollapsibleTrigger,
    CollapsibleContent,
} from "reka-ui";
import { defineProps } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import roundMarker from "../assets/round_marker.webp";

const flagIcon = L.icon({
    iconUrl: roundMarker,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
});



const route = useRoute();
const router = useRouter();
const userId = route.params.id;

export interface DuelData {
    id: string;
    mode: string;
    start_time: number;
    ranked: boolean;
    map: Map;
    rounds: Round[];
    elo_histories: EloHistory[];
    player1: Player;
    player2: Player;
    winner_id: string;
    loser_id: string;
}

export interface Map {
    id: string;
    name: string;
}

export interface Round {
    id: string;
    round_number: number;
    player1_hp_before: number;
    player2_hp_before: number;
    player1_hp_after: number;
    player2_hp_after: number;
    panorama: Panorama;
    guesses: Guess[];
}

export interface Panorama {
    id: string;
    lat: number;
    lng: number;
    country_code: string;
    heading: number;
    pitch: number;
    zoom: number;
}

export interface Guess {
    round_id: string;
    player_id: string;
    lat: number;
    lng: number;
    distance: number;
    score: number;
}

export interface Player {
    id: string;
    username: string;
    country_code: string;
    rating: number;
    avatar_url: string;
    pin_url: string | null;
}

export interface EloHistory {
    id: string;
    user_id: string;
    duel_id: string;
    datetime: number;
    elo_before: number;
    elo_after: number;
}

const props = defineProps<{ duel: DuelData }>();

let map: L.Map | null = null;
let markers: L.Marker[] = [];
let player1Icon = ref<L.divIcon | null>(null);
let player2Icon = ref<L.divIcon | null>(null);

const userEloChange = computed(() => {
  const record = props.duel.elo_histories.find(e => e.user_id === userId)
  if (!record) return null
  const diff = record.elo_after - record.elo_before
  return diff > 0 ? `+${diff}` : `${diff}`
})

function initMap() {
    nextTick(() => {
        const mapId = `map-${props.duel.id}`;
        const el = document.getElementById(mapId);
        
        if (!el) return;
        
        if (el._leaflet_id) return;
        
        const firstRound = props.duel.rounds[0];
        map = L.map(mapId).setView(
        [firstRound.panorama.lat, firstRound.panorama.lng],
        3
        );
        
        L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
            maxZoom: 19,
            attribution: '© OpenFreeMap / © OpenStreetMap contributors',
        }).addTo(map);
        
        player1Icon = L.divIcon({
            className: "custom-player-icon", 
            html: `
                <div class="relative w-10 h-10 rounded-full overflow-hidden border-3 border-white bg-gray-200">
                <img 
                    src="https://www.geoguessr.com/images/resize:auto:100:100/gravity:ce/plain/${props.duel.player1.avatar_url}" 
                    alt="avatar"
                    class="absolute top-0 left-1/2 -translate-x-1/2 w-auto h-[170%] object-cover"
                />
                </div>
      `,
            iconSize: [48, 48],
            iconAnchor: [24, 24],
        });

        player2Icon = L.divIcon({
            className: "custom-player-icon",
            html: `
                <div class="relative w-10 h-10 rounded-full overflow-hidden border-3 border-white bg-gray-200">
                <img 
                    src="https://www.geoguessr.com/images/resize:auto:100:100/gravity:ce/plain/${props.duel.player2.avatar_url}" 
                    alt="avatar"
                    class="absolute top-0 left-1/2 -translate-x-1/2 w-auto h-[170%] object-cover"
                />
                </div>
      `,
            iconSize: [48, 48],
            iconAnchor: [24, 24],
        });
        
        updateMap(firstRound);
    });
}

function updateMap(round: Round) {
    if (!map) return;
    
    markers.forEach((m) => m.remove());
    markers = [];
    
    const panoMarker = L.marker(
    [round.panorama.lat, round.panorama.lng],
    { icon: flagIcon }, 
    ).on("click", () => openStreetView(round.panorama)).addTo(map);
    markers.push(panoMarker);
    
    round.guesses.forEach((guess) => {
        const player =
        guess.player_id === props.duel.player1.id
        ? props.duel.player1
        : props.duel.player2;
        
        const color = player.id === props.duel.player1.id ? "#22c55e" : "#ef4444";
        
        const icon = player.id === props.duel.player1.id ? player1Icon : player2Icon
        
        const marker = L.marker([guess.lat, guess.lng], { icon })
        .bindPopup(`<b>${player.username}</b><br>${guess.score} pts`)
        .addTo(map);
        
        markers.push(marker);

        const line = L.polyline(
            [
                [guess.lat, guess.lng],
                [round.panorama.lat, round.panorama.lng],
            ],
            {
                color: "black",
                weight: 2,
                dashArray: "2,4",
                lineCap: "square",
                lineJoin: "square",
            }
        ).addTo(map);
        markers.push(line);
    });
    
    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.5));
}

function openStreetView(panorama: Panorama) {
  window.open(`https://maps.google.com/maps?layer=c&cbll=${panorama.lat},${panorama.lng}`);
}

function getGuess(round: Round, playerId: string): Guess | null {
  return round.guesses.find(g => g.player_id === playerId) || null
}

function goToProfile(userId: string) {
  router.push(`/users/${userId}`)
}
</script>

<template>
    <div class="glass">
        <CollapsibleRoot @click="initMap()">
            <CollapsibleTrigger
            class="glass flex justify-between items-center w-full p-4 cursor-pointer transition duration-300"
            :class="
            userId === duel.winner_id
            ? 'glow-green-xl hover:bg-green-400/10'
            : 'glow-red-xl hover:bg-red-400/10'
            "
            >
            <span class="font-semibold">{{ duel.mode }}</span>
            
            <div class="font-semibold flex gap-3 items-center">
                <div
                :class="
                duel.winner_id === duel.player1.id
                ? 'text-green-400'
                : 'text-red-400'
                "
                >
                {{ duel.rounds[duel.rounds.length - 1].player1_hp_after }}
            </div>
            <div :class="userId !== duel.player1.id ? 'cursor-pointer hover:underline' : ''" @click.stop="userId !== duel.player1.id ? goToProfile(duel.player1.id) : ''">
              {{ duel.player1.username }}
            </div>
            <span class="text-gray-400">VS</span>
            <div :class="userId !== duel.player2.id ? 'cursor-pointer hover:underline' : ''" @click.stop="userId !== duel.player2.id ? goToProfile(duel.player2.id) : ''">
              {{ duel.player2.username }}
            </div>
            <div
            :class="
            duel.winner_id === duel.player2.id
            ? 'text-green-400'
            : 'text-red-400'
            "
            >
            {{ duel.rounds[duel.rounds.length - 1].player2_hp_after }}
        </div>
    </div>
    
    <span
    class="font-semibold"
    :class="duel.ranked ? userEloChange >= 0 ? 'text-green-400': 'text-red-400' : 'text-gray-400'"
    >
    {{ duel.ranked ? userEloChange : 'UNRANKED' }}
</span>
</CollapsibleTrigger>

<CollapsibleContent
class="gap-0 flex flex-col transition-all duration-300"
>
<div :id="`map-${duel.id}`" class="w-full h-64 rounded-xl"></div>

<div
v-for="round in duel.rounds"
:key="round.id"
@click="updateMap(round)"
class="bg-black/20 p-3 flex justify-between items-center hover:bg-black/40 transition cursor-pointer"
>

<div class="flex flex-col">
  <span class="text-gray-300 font-semibold">{{ duel.player1.username }}</span>
  <div class="flex gap-2 text-xs text-gray-400 items-center">
    <span
      :class="round.player1_hp_after < round.player1_hp_before ? 'text-red-400' : 'text-green-400'"
    >
      {{ round.player1_hp_after }} HP
    </span>
    <span v-if="round.player1_hp_before !== round.player1_hp_after">
      -{{ Math.abs(round.player1_hp_before - round.player1_hp_after) }}
    </span>

    <template v-if="getGuess(round, duel.player1.id)">
      <span>{{ (getGuess(round, duel.player1.id).distance / 1000).toFixed(1) }} km</span>
      <span>{{ getGuess(round, duel.player1.id).score }} pts</span>
    </template>

    <template v-else>
      <span class="text-gray-500 italic">No guess</span>
    </template>
  </div>
</div>




<div
class="absolute left-1/2 transform translate-x-18 flex items-center gap-2 text-xs text-gray-400"
>
<span>ROUND {{ round.round_number }}</span>
<span class="uppercase">{{ round.panorama.country_code }}</span>
</div>


<div class="flex flex-col items-end">
  <span class="text-gray-300 font-semibold">{{ duel.player2.username }}</span>
  <div class="flex gap-2 text-xs text-gray-400 items-center justify-end">
    <template v-if="getGuess(round, duel.player2.id)">
      <span>{{ getGuess(round, duel.player2.id).score }} pts</span>
      <span>{{ (getGuess(round, duel.player2.id).distance / 1000).toFixed(1) }} km</span>
    </template>

    <template v-else>
      <span class="text-gray-500 italic">No guess</span>
    </template>

    <span v-if="round.player2_hp_before !== round.player2_hp_after">
      -{{ Math.abs(round.player2_hp_before - round.player2_hp_after) }}
    </span>
    <span
      :class="round.player2_hp_after < round.player2_hp_before ? 'text-red-400' : 'text-green-400'"
    >
      {{ round.player2_hp_after }} HP
    </span>
  </div>
</div>
</div>
</CollapsibleContent>
</CollapsibleRoot>
</div>
</template>
