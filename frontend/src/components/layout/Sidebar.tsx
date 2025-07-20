// frontend/src/components/layout/Sidebar.tsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  BookOpen, 
  FileText, 
  BarChart3, 
  Users, 
  Settings,
  ChevronRight,
  ChevronDown 
} from 'lucide-react';
import { usePermissions } from '@/hooks/usePermissions';
import { RoleBasedComponent } from '@/components/auth';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const iconMap: Record<string, React.ComponentType<any>> = {
  Home,
  BookOpen,
  FileText,
  BarChart3,
  Users,
  Settings,
};

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { getAccessibleMenus } = usePermissions();
  const [expandedMenus, setExpandedMenus] = React.useState<Set<string>>(new Set());

  const menus = getAccessibleMenus();

  const toggleMenu = (menuKey: string) => {
    const newExpanded = new Set(expandedMenus);
    if (newExpanded.has(menuKey)) {
      newExpanded.delete(menuKey);
    } else {
      newExpanded.add(menuKey);
    }
    setExpandedMenus(newExpanded);
  };

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const renderMenuItem = (menu: any, depth = 0) => {
    const hasChildren = menu.children && menu.children.length > 0;
    const isExpanded = expandedMenus.has(menu.key);
    const Icon = iconMap[menu.icon] || Home;

    return (
      <div key={menu.key}>
        {menu.path ? (
          <Link
            to={menu.path}
            className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              isActive(menu.path)
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
            style={{ paddingLeft: `${16 + depth * 16}px` }}
            onClick={onClose}
          >
            <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
            {menu.label}
          </Link>
        ) : (
          <button
            onClick={() => toggleMenu(menu.key)}
            className={`w-full flex items-center justify-between px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
            style={{ paddingLeft: `${16 + depth * 16}px` }}
          >
            <div className="flex items-center">
              <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
              {menu.label}
            </div>
            {hasChildren && (
              isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )
            )}
          </button>
        )}

        {hasChildren && isExpanded && (
          <div className="ml-4">
            {menu.children.map((child: any) => renderMenuItem(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* 移动端遮罩 */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          onClick={onClose}
        >
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
        </div>
      )}

      {/* 侧边栏 */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* 头部 */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
            <span className="text-lg font-semibold text-gray-900">导航菜单</span>
            <button
              onClick={onClose}
              className="lg:hidden text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>

          {/* 菜单列表 */}
          <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
            {menus.map(menu => renderMenuItem(menu))}
          </nav>
        </div>
      </div>
    </>
  );
};

export default Sidebar;