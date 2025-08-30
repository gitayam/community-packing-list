#!/usr/bin/env python3
import re

# Read the template file
with open('packing_lists/templates/packing_lists/packing_list_detail.html', 'r') as f:
    content = f.read()

# Find and replace the pricing section
old_pattern = r'<div class="price-info">\s*{% if item_wp\.prices_with_votes %}.*?{% endif %}\s*</div>'

new_pricing = '''<div class="price-info price-info-compact">
                                    {% if item_wp.prices_with_votes %}
                                        {% with first_price=item_wp.prices_with_votes.0 %}
                                        <div class="price-summary" onclick="togglePriceDetails(this)">
                                            <span class="best-value-indicator">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-award"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 17 17 23 15.79 13.88"></polyline></svg>
                                                BEST VALUE
                                            </span>
                                            <strong>${{ first_price.price.price }}</strong> at {{ first_price.price.store.name }}
                                            {% if item_wp.prices_with_votes|length > 1 %}
                                                <span class="more-prices-indicator">(+{{ item_wp.prices_with_votes|length|add:"-1" }} more)</span>
                                                <svg class="expand-icon" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                                            {% endif %}
                                        </div>
                                        {% if item_wp.prices_with_votes|length > 1 %}
                                        <div class="price-details" style="display: none;">
                                            <ul>
                                            {% for price_data in item_wp.prices_with_votes %}
                                                <li class="{% if forloop.first %}best-value{% endif %}">
                                                    <strong>${{ price_data.price.price }}</strong> for {{ price_data.price.quantity }} at {{ price_data.price.store.name }}
                                                    {% if price_data.price.date_purchased %}({{ price_data.price.date_purchased|date:"Y-m-d" }}){% endif %}
                                                    <br>
                                                    <small>
                                                        <span class="text-muted">${{ price_data.price_per_unit|floatformat:2 }}/unit</span>
                                                        {% if price_data.vote_confidence > 0 %}
                                                            <span class="text-success">• High confidence</span>
                                                        {% elif price_data.vote_confidence < 0 %}
                                                            <span class="text-danger">• Low confidence</span>
                                                        {% else %}
                                                            <span class="text-warning">• No votes yet</span>
                                                        {% endif %}
                                                    </small>
                                                    
                                                    <div class="vote-buttons">
                                                        <form method="post" style="display: inline;">
                                                            {% csrf_token %}
                                                            <input type="hidden" name="upvote_price" value="{{ price_data.price.id }}">
                                                            <button type="submit" class="button button-icon-sm" title="Upvote this price">
                                                                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-chevron-up"><polyline points="18 15 12 9 6 15"></polyline></svg>
                                                            </button>
                                                        </form>
                                                        <span class="vote-count">{{ price_data.upvotes }}</span>
                                                        
                                                        <form method="post" style="display: inline;">
                                                            {% csrf_token %}
                                                            <input type="hidden" name="downvote_price" value="{{ price_data.price.id }}">
                                                            <button type="submit" class="button button-icon-sm" title="Downvote this price">
                                                                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-chevron-down"><polyline points="6 9 12 15 18 9"></polyline></svg>
                                                            </button>
                                                        </form>
                                                        <span class="vote-count">{{ price_data.downvotes }}</span>
                                                    </div>
                                                </li>
                                            {% endfor %}
                                            </ul>
                                        </div>
                                        {% endif %}
                                        {% endwith %}
                                    {% else %}
                                        <p class="no-prices">No pricing information yet.</p>
                                    {% endif %}
                                    <a href="/item/{{ item_wp.item.id }}/add_price/to_list/{{ packing_list.id }}/" class="button text-small mt-1 add-price-modal-link" data-url="/item/{{ item_wp.item.id }}/add_price_modal/to_list/{{ packing_list.id }}/">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-plus-circle"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line></svg>
                                        Add Price
                                    </a>
                                </div>'''

# Use a more specific replacement
content_lines = content.split('\n')
new_lines = []
in_price_info = False
skip_lines = 0

for i, line in enumerate(content_lines):
    if skip_lines > 0:
        skip_lines -= 1
        continue
        
    if '<div class="price-info">' in line:
        # Find the end of this price-info block
        indent = len(line) - len(line.lstrip())
        end_found = False
        j = i + 1
        brace_count = 1
        
        while j < len(content_lines) and not end_found:
            if '{% if' in content_lines[j]:
                brace_count += 1
            if '{% endif %}' in content_lines[j]:
                brace_count -= 1
                if brace_count == 0:
                    # Check for the closing div
                    k = j + 1
                    while k < len(content_lines):
                        if '</div>' in content_lines[k] and content_lines[k].lstrip().startswith('</div>'):
                            end_found = True
                            skip_lines = k - i
                            break
                        elif content_lines[k].strip() and not content_lines[k].lstrip().startswith('<'):
                            break
                        k += 1
            j += 1
        
        # Add the new pricing HTML with proper indentation
        indent_str = ' ' * indent
        for new_line in new_pricing.split('\n'):
            if new_line.strip():
                new_lines.append(indent_str + new_line.strip())
    else:
        new_lines.append(line)

# Write the modified content
with open('packing_lists/templates/packing_lists/packing_list_detail.html', 'w') as f:
    f.write('\n'.join(new_lines))

print("Template updated successfully!")