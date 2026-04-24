export function QrShowcase({ table, featuredItems, qrImageUrl }) {
  const qrLabel = table?.label || 'Hotel Menu'
  const qrPath = table?.path || '/'

  return (
    <div className="hero-device">
      <div className="device-header">
        <span className="live-dot"></span>
        <p>{qrPath}</p>
      </div>

      <div className="device-qr-card">
        <div className="qr-preview-shell">
          {qrImageUrl ? (
            <img className="qr-preview-image" src={qrImageUrl} alt={`${qrLabel} QR code`} />
          ) : (
            <div className="qr-preview-fallback" aria-hidden="true"></div>
          )}
        </div>
        <div>
          <p className="mini-label">Live table access</p>
          <strong>{qrLabel} QR</strong>
          <p>Guests scan once and always see the latest hotel menu and availability.</p>
        </div>
      </div>

      <div className="device-preview-list">
        {featuredItems.map((item) => (
          <article key={item.id}>
            <img src={item.image} alt={item.name} />
            <div>
              <strong>{item.name}</strong>
              <span>{item.category}</span>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
