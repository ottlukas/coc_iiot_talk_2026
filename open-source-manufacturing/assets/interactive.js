// Interactive helpers for reveal-full.md
(function(){
  // pipeline step click handler: show a short note
  function onStepClick(e){
    const t = e.currentTarget;
    const step = t.getAttribute('data-step');
    const note = document.getElementById('pipeline-note');
    if(!note) return;
    // toggle active state
    document.querySelectorAll('.pipeline-step').forEach(btn=>btn.classList.remove('active'));
    t.classList.add('active');
    note.style.display = 'block';
    note.innerHTML = '<strong>'+step+'</strong> — Clicked. Example responsibilities: ' + {
      'PLC4X':'edge protocol adapters, low-latency collection',
      'BifroMQ':'MQTT broker and buffering',
      'Kafka':'durable streaming and partitioning',
      'Flink/Beam':'stream validation and enrichment',
      'IoTDB':'high-throughput time-series storage (TSFile)',
      'Iceberg':'cold cataloged lake storage',
      'Superset':'analytics and reproducible dashboards'
    }[step] + '.';
  }

  document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.pipeline-step').forEach(btn=>btn.addEventListener('click', onStepClick));

    // Make fragments reveal nicely when using reveal.js
    if(window.Reveal){
      Reveal.addEventListener('fragmentshown', function(e){
        e.fragment.classList.add('revealed');
      });
      Reveal.addEventListener('fragmenthidden', function(e){
        e.fragment.classList.remove('revealed');
      });
    }
  });
})();
