<template>
  <svg class="flex-1" ref="svgRef" />
</template>

<script>
import { Markmap } from 'markmap-view';
import { Transformer } from 'markmap-lib';

export default {
  name: 'App',
  props: ['markdown'],
  data() {
    return {
      value: '',
    };
  },
  watch: {
    markdown(newVal, oldVal) {
      this.update();
    }
  },
  methods: {
    update() {
      const transformer = new Transformer();
      const { root } = transformer.transform(this.markdown);
      this.mm.setData(root);
      this.mm.fit();
    },
  },
  mounted() {
    this.mm = Markmap.create(this.$refs.svgRef);
    this.update();
  },
};
</script>
