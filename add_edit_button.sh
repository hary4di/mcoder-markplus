#!/bin/bash
# Add Edit button to users.html Actions column

echo "=== Adding Edit Button to Production Template ==="
echo ""

cd /opt/markplus/mcoder-markplus/app/templates

# Backup
cp users.html users.html.before_edit_btn

# Find line with delete button and add edit button before it
# Current structure (line ~66-72):
#   <td>
#       {% if user.id != current_user.id %}
#       <button class="btn btn-sm btn-outline-danger" title="Delete user">
#           <i class="bi bi-trash"></i>
#       </button>
#       {% endif %}
#   </td>

# Replace entire Actions cell with new structure including edit button
sed -i '66,72s|<td>|<td>\n                                <div class="d-flex gap-1">|' users.html
sed -i '67 i\                                    {% if not user.is_super_admin or current_user.is_super_admin %}\n                                    <a href="{{ url_for('\''auth.edit_user'\'', user_id=user.id) }}" class="btn btn-sm btn-outline-primary" title="Edit user">\n                                        <i class="bi bi-pencil"></i>\n                                    </a>\n                                    {% endif %}' users.html
sed -i 's|</button>$|</button>\n                                </div>|' users.html

echo "✅ Edit button added"
echo "Backup: users.html.before_edit_btn"
echo ""
echo "Restarting application..."
supervisorctl restart mcoder-markplus

echo ""
echo "Done! Check: https://m-coder.flazinsight.com/users"
