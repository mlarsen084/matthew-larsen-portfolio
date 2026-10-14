(() => {
  'use strict';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('.gallery').forEach(gallery => {
    const rail = gallery.querySelector('.rail');
    const controls = gallery.querySelector('.rail-controls');
    const previous = controls.querySelector('[data-direction="-1"]');
    const next = controls.querySelector('[data-direction="1"]');
    const counter = controls.querySelector('.rail-count');
    const items = [...rail.children];
    controls.hidden = false;
    let scheduled = false;
    function update() {
      scheduled = false;
      const remaining = rail.scrollWidth - rail.clientWidth - rail.scrollLeft;
      previous.disabled = rail.scrollLeft < 3;
      next.disabled = remaining < 3;
      const relative = rail.getBoundingClientRect();
      const closest = items.reduce((best, item, index) => {
        const distance = Math.abs(item.getBoundingClientRect().left - relative.left);
        return distance < best.distance ? { distance, index } : best;
      }, { distance: Infinity, index: 0 });
      counter.textContent = `${closest.index + 1} / ${items.length}`;
    }
    controls.addEventListener('click', event => {
      const button = event.target.closest('[data-direction]');
      if (!button || button.disabled) return;
      const step = items[0].getBoundingClientRect().width + parseFloat(getComputedStyle(rail).gap);
      rail.scrollBy({ left: Number(button.dataset.direction) * step, behavior: reduceMotion.matches ? 'instant' : 'smooth' });
    });
    rail.addEventListener('scroll', () => {
      if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
    }, { passive: true });
    const observer = new ResizeObserver(update);
    observer.observe(rail);
    update();
  });

  const dialog = document.querySelector('.media-dialog');
  const content = dialog.querySelector('.dialog-content');
  const title = dialog.querySelector('#dialog-title');
  const caption = dialog.querySelector('.dialog-caption');
  const imageControls = dialog.querySelector('.image-controls');
  const imageCounter = dialog.querySelector('.image-count');
  const prevImage = dialog.querySelector('.image-prev');
  const nextImage = dialog.querySelector('.image-next');
  let collection = [];
  let activeIndex = 0;
  let trigger = null;
  let generation = 0;

  function cleanup() {
    generation += 1;
    content.querySelectorAll('video').forEach(video => {
      video.pause();
      video.removeAttribute('src');
      video.load();
    });
    content.replaceChildren();
  }

  function showImage(index) {
    activeIndex = Math.max(0, Math.min(collection.length - 1, index));
    const button = collection[activeIndex];
    cleanup();
    const version = generation;
    const image = new Image();
    image.alt = button.dataset.alt;
    image.src = button.dataset.image;
    image.addEventListener('error', () => {
      if (generation === version) content.textContent = 'The image couldn’t be loaded. Please try again.';
    }, { once: true });
    title.textContent = button.dataset.title;
    caption.textContent = button.dataset.alt;
    content.append(image);
    imageControls.hidden = collection.length < 2;
    prevImage.disabled = activeIndex === 0;
    nextImage.disabled = activeIndex === collection.length - 1;
    imageCounter.textContent = `${activeIndex + 1} / ${collection.length}`;
  }

  function showVideo(button) {
    cleanup();
    const version = generation;
    collection = [];
    imageControls.hidden = true;
    title.textContent = button.dataset.title;
    caption.textContent = button.dataset.youtube ? 'Campaign film · YouTube' : 'Editing & final production by Matthew Larsen';
    if (button.dataset.video) {
      const video = document.createElement('video');
      video.controls = true;
      video.playsInline = true;
      video.preload = 'none';
      video.src = button.dataset.video;
      video.setAttribute('aria-label', button.dataset.title);
      const poster = button.querySelector('img');
      if (poster) video.poster = poster.currentSrc || poster.src;
      video.addEventListener('error', () => {
        if (generation !== version) return;
        const error = document.createElement('p');
        error.className = 'dialog-error';
        error.textContent = 'This video couldn’t be played here. ';
        const link = document.createElement('a');
        link.href = button.dataset.video;
        link.textContent = 'Open the video directly ↗';
        error.append(link);
        content.replaceChildren(error);
      }, { once: true });
      content.append(video);
      video.play().catch(() => { /* Native controls remain available if autoplay is declined. */ });
    } else {
      const iframe = document.createElement('iframe');
      iframe.title = button.dataset.title;
      iframe.src = `https://www.youtube-nocookie.com/embed/${button.dataset.youtube}?autoplay=1&rel=0`;
      iframe.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      iframe.allowFullscreen = true;
      iframe.referrerPolicy = 'strict-origin-when-cross-origin';
      content.append(iframe);
      const link = document.createElement('a');
      link.href = `https://www.youtube.com/watch?v=${button.dataset.youtube}`;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = 'Watch on YouTube ↗';
      link.className = 'text-link';
      content.append(link);
    }
  }

  document.addEventListener('click', event => {
    const button = event.target.closest('.media-trigger');
    if (!button) return;
    trigger = button;
    if (button.dataset.image) {
      const group = button.closest('.project') || button.closest('.gallery');
      collection = [...group.querySelectorAll('[data-image]')];
      showImage(collection.indexOf(button));
    } else showVideo(button);
    if (!dialog.open) dialog.showModal();
    document.body.classList.add('modal-open');
  });
  dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    cleanup();
    document.body.classList.remove('modal-open');
    if (trigger?.isConnected) trigger.focus({ preventScroll: true });
  });
  prevImage.addEventListener('click', () => showImage(activeIndex - 1));
  nextImage.addEventListener('click', () => showImage(activeIndex + 1));
  dialog.addEventListener('keydown', event => {
    if (!collection.length || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    showImage(activeIndex + (event.key === 'ArrowLeft' ? -1 : 1));
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) content.querySelector('video')?.pause();
  });
})();
