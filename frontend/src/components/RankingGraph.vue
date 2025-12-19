<script setup>
import { Trophy } from "lucide-vue-next"
import { fetchRankingGraphData } from "../api"
import { ref, onMounted, computed, watch } from "vue"
import VueECharts from "vue-echarts"
import * as echarts from "echarts"

const props = defineProps({
    userId: {
        type: String,
        required: true
    }
})

echarts.registerTheme("dark", {
    backgroundColor: "transparent"
})

const rawData = ref([])

const sortedData = computed(() =>
[...rawData.value].sort((a, b) => a.timestamp - b.timestamp)
)

let values = ref([]);
let minElo = ref();
let maxElo = ref();
let winNb = ref();
let losNb = ref();

const option = computed(() => {
    return {
        grid: {
            top: 0,
            bottom: 0,
            left: 0,
            right: 0,
            containLabel: false
        },
        tooltip: {
            trigger: "axis",
            formatter: params => {
                const index = params[0].dataIndex
                const d = sortedData.value[index]
                const date = new Date(d.timestamp)
                return `<b>${date.toLocaleString()}</b><br/>ELO: ${d.elo}`
            }
        },
        xAxis: {
            type: "category",
            data: sortedData.value.map(d => new Date(d.timestamp).toLocaleTimeString()),
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { show: false },
            splitLine: { show: false }
        },
        yAxis: {
            type: "value",
            min: minElo - 10,
            max: maxElo + 10,
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { show: false },
            splitLine: {
                show: true,
                lineStyle: {
                    color: 'rgba(29, 219, 79, 0.2)', 
                    width: 0.5,
                    type: [4, 3] // 20px dash, 20px gap
                }
            },
            splitNumber: 6,
            boundaryGap: false
            
        },
        series: [
        {
            data: sortedData.value.map(d => d.elo),
            type: "line",
            smooth: false,
            showSymbol: false,
            lineStyle: { color: "#42b983", width: 2 },
            areaStyle: { color: "rgba(66, 185, 131, 0.2)" }
        }
        ],
    }
})


async function loadRankingData() {
    if (!props.userId) return
    rawData.value = await fetchRankingGraphData(props.userId)
    values = sortedData.value.map(d => d.elo)
    minElo = Math.min(...values)
    maxElo = Math.max(...values)
    
    winNb = 0
    losNb = 0
    for (let i = 1; i < sortedData.value.length; i++) {
        if (sortedData.value[i].elo > sortedData.value[i - 1].elo) {
            winNb++
        } else if (sortedData.value[i].elo < sortedData.value[i - 1].elo) {
            losNb++
        }
    }
}

onMounted(loadRankingData)

watch(() => props.userId, loadRankingData)
</script>

<template>
    <div class=" flex items-center gap-2 justify-between">
        <div class="text-gray-400 flex items-center gap-2">
            <Trophy class="w-4 h-4" />
            Rating Solo
        </div>
        <div>
            {{ rawData.length ? sortedData[sortedData.length - 1].elo + ' rating': 'N/A' }}
        </div>
    </div>
    <div class="text-xs flex justify-between">
        <div class="flex gap-2">
            <div class="text-gray-400">
                PEAK 
            </div>
            <div>
                {{ maxElo }}
            </div>
        </div>
        <div>
            {{ winNb + "W-" }}
            {{ losNb  + "L" }}
            {{ '(' + (winNb / (winNb + losNb) * 100).toFixed(0) + '%)' }}
        </div>
    </div>
    <h2 v-if="!rawData.length" class="font-semibold">UNRANKED</h2>
    <div v-else class="w-full h-34">
        <VueECharts :option="option" autoresize />
    </div>
</template>
