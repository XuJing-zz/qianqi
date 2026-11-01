<!-- 全站页脚：版权信息、备案号、快捷链接，以及底部装饰性的悬浮卡片 -->
<template>

    <div class="bodybox">

        <!-- 版权、备案号与快捷链接 -->
        <div class="foot-text">
            <div class="main">
                © 2026 {{ brandName }}
            </div>
            <div v-if="icp" class="main foot-icp">{{ icp }}</div>

            <div class="nav">
                <ul>
                    <li><router-link to="/about">关于我们</router-link></li>
                    <li><router-link to="/contact">联系我们</router-link></li>
                    <li><router-link to="/agreement">用户协议</router-link></li>
                </ul>
            </div>
        </div>

        <!-- 装饰性卡片带：鼠标移动时让附近的卡片微微抬起，形成波浪效果 -->
        <div class="hover-up" ref="hoverUpBox"><div v-for="(item, i) in cards" :key="i" class="hover-card" :class="{ active: activeIndex === i }" @mousemove="onCardMove(i, $event)"></div></div>

    </div>



</template>

<script>
import { systemConfig } from '@/store'

/* 页脚组件：使用 Options API 写法，data 存放状态，computed 派生展示数据 */
export default {
    data() {
        return {
            // 当前鼠标悬停的卡片下标，-1 表示没有悬停
            activeIndex: -1,
            // 装饰卡片总数
            count: 50,
        }
    },
    computed: {
        /* 生成指定数量的占位卡片，模板只需按下标循环 */
        cards() {
            return new Array(this.count).fill(0)
        },
        /* 品牌名称与备案号来自系统配置，未配置时提供默认值 */
        brandName() {
            return systemConfig.systemName || '漆器非遗传承平台'
        },
        icp() {
            return systemConfig.icp || ''
        },
    },
    methods: {
        /* 鼠标移动到某张卡片时记录下标，并重新计算整排卡片高度 */
        onCardMove(index) {
            if (this.activeIndex !== index) {
                this.activeIndex = index
                this.applyArc(index)
            }
        },
        /* 根据鼠标所在位置，用高斯函数计算每张卡片的抬升高度：越近抬得越高 */
        applyArc(index) {
            // 获取页脚中所有装饰卡片元素
            const cards = this.$refs.hoverUpBox?.querySelectorAll('.hover-card')
            if (!cards) return
            cards.forEach((el, i) => {
                if (index === -1) {
                    // 没有悬停时恢复默认高度
                    el.style.height = ''
                    return
                }
                const dist = Math.abs(i - index)
                // 距离越远，抬升量按指数衰减
                const lift = 35 * Math.exp(-(dist * dist) / 30)
                el.style.height = `calc(100% + ${lift.toFixed(1)}px)`
                el.style.transition = 'height 0.25s cubic-bezier(0.2, 0.7, 0.3, 1)'
            })
        },
    },
}
</script>

<style src="./foot.css"></style>
