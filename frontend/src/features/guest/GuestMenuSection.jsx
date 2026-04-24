import { SectionHeading } from '../../components/SectionHeading.jsx'

export function GuestMenuSection({
  categories,
  activeCategory,
  setActiveCategory,
  showAvailableOnly,
  setShowAvailableOnly,
  visibleItems,
  restaurant,
  currentTableLabel,
  statusMessage,
  errorMessage,
}) {
  const guestMenuTitle = currentTableLabel || 'Hotel Menu'

  return (
    <section id="guest-menu" className="panel section-panel">
      <SectionHeading
        eyebrow="Customer View"
        title={guestMenuTitle}
        description="Built mobile-first for fast scanning, clear categories, and quick decisions at the table."
        action={
          <label className="switch-row">
            <input
              type="checkbox"
              checked={showAvailableOnly}
              onChange={() => setShowAvailableOnly((current) => !current)}
            />
            <span>Available only</span>
          </label>
        }
      />

      <div className="chip-row" role="tablist" aria-label="Menu categories">
        <button
          type="button"
          className={activeCategory === 'All' ? 'active' : ''}
          onClick={() => setActiveCategory('All')}
        >
          All
        </button>
        {categories.map((category) => (
          <button
            key={category.id}
            type="button"
            className={activeCategory === category.name ? 'active' : ''}
            onClick={() => setActiveCategory(category.name)}
          >
            {category.name}
          </button>
        ))}
      </div>

      {statusMessage ? <p className="status-banner">{statusMessage}</p> : null}
      {errorMessage ? <p className="error-banner">{errorMessage}</p> : null}

      <div className="menu-grid">
        {visibleItems.map((item) => (
          <article key={item.id} className="menu-card">
            <img src={item.image} alt={item.name} />
            <div className="menu-card-body">
              <div className="menu-meta">
                <span>{item.category}</span>
                <mark className={item.available ? '' : 'sold-out'}>
                  {item.available ? 'Available now' : 'Unavailable'}
                </mark>
              </div>

              <h3>{item.name}</h3>
              <p>{item.description}</p>

              <div className="menu-footer">
                <strong>
                  {item.price} {restaurant?.currency || 'ETB'}
                </strong>
                <div className="tag-row">
                  {item.spicy ? <small>Spicy</small> : null}
                  {item.featured ? <small>Chef pick</small> : null}
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
